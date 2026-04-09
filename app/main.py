import os
import re
import secrets
import sys
from contextlib import asynccontextmanager

import httpx
import sentry_sdk

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.shared import templates, translations, SUPPORTED_LANGS
from app.routers import public, api
from app.limiter import limiter

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CURRENT_ENV = os.getenv("ENVIRONMENT", "dev")
TURNSTILE_SITE_KEY = os.getenv("TURNSTILE_SITE_KEY", "")
CLOUDFLARE_WEB_ANALYTICS_TOKEN = os.getenv("CLOUDFLARE_WEB_ANALYTICS_TOKEN", "")
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
CMS_API_BASE_URL = os.getenv("CMS_API_BASE_URL", "http://host.docker.internal:8004")
_cms_public_origin_raw = os.getenv("CMS_PUBLIC_ORIGIN", "http://localhost:8004")

_VALID_ORIGIN_RE = re.compile(r"^https?://[a-zA-Z0-9._:/-]+\Z")
if not _VALID_ORIGIN_RE.match(_cms_public_origin_raw):
    print(
        f"FATAL: CMS_PUBLIC_ORIGIN '{_cms_public_origin_raw}' is not a valid "
        "http(s) origin. Check your .env file. Refusing to start.",
        file=sys.stderr,
    )
    sys.exit(1)

CMS_PUBLIC_ORIGIN = _cms_public_origin_raw

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        enable_tracing=True,
        traces_sample_rate=0.05,   # 5% sample — sufficient for latency profiling
        send_default_pii=False,    # do not attach visitor IPs or request bodies
        environment=CURRENT_ENV,
        integrations=[
            StarletteIntegration(transaction_style="url"),
            FastApiIntegration(transaction_style="url"),
        ],
    )

# ---------------------------------------------------------------------------
# Lifespan — manages the shared httpx client
# ---------------------------------------------------------------------------

async def _load_cloudflare_networks(
    client: httpx.AsyncClient,
) -> list:
    """Fetch Cloudflare's authoritative IP ranges at startup.

    Falls back to the hardcoded CF_FALLBACK_NETWORKS list in limiter.py if
    either URL is unreachable, so a Cloudflare outage never prevents the app
    from starting — and the rate-limiter's IP-trust logic remains operative.
    """
    import ipaddress
    from app.limiter import CF_FALLBACK_NETWORKS

    urls = [
        "https://www.cloudflare.com/ips-v4",
        "https://www.cloudflare.com/ips-v6",
    ]
    networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
    try:
        for url in urls:
            resp = await client.get(url, timeout=5.0)
            resp.raise_for_status()
            for line in resp.text.splitlines():
                line = line.strip()
                if line:
                    networks.append(ipaddress.ip_network(line, strict=False))
        print(f"[startup] Loaded {len(networks)} Cloudflare IP networks.")
        return networks
    except Exception as e:
        print(
            f"[startup] WARNING: Could not fetch Cloudflare IP ranges ({e}). "
            "Falling back to hardcoded list — rate-limiter trust logic is still active."
        )
        return CF_FALLBACK_NETWORKS


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create one shared AsyncClient for the process lifetime.

    Re-using a single client is more efficient than opening a new TCP connection
    on every incoming request (connection pooling, keep-alive, DNS caching).
    """
    app.state.http_client = httpx.AsyncClient()
    app.state.cms_base_url = CMS_API_BASE_URL
    app.state.cms_public_origin = CMS_PUBLIC_ORIGIN
    app.state.cloudflare_networks = await _load_cloudflare_networks(
        app.state.http_client
    )
    yield
    await app.state.http_client.aclose()


# ---------------------------------------------------------------------------
# App & static files
# ---------------------------------------------------------------------------
app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Expose runtime globals to all Jinja2 templates
templates.env.globals["env"] = CURRENT_ENV
templates.env.globals["turnstile_site_key"] = TURNSTILE_SITE_KEY
templates.env.globals["cloudflare_web_analytics_token"] = CLOUDFLARE_WEB_ANALYTICS_TOKEN

# ---------------------------------------------------------------------------
# Middleware (order matters: last added = outermost)
# ---------------------------------------------------------------------------

class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests whose body exceeds MAX_BODY_BYTES.

    Two-path enforcement:
    1. Fast-path — Content-Length header declared: short-circuit before reading
       any body bytes, returning 413 immediately.
    2. Slow-path — chunked transfer encoding or missing Content-Length: wrap the
       raw ASGI receive callable so each chunk is counted cumulatively. When the
       running total exceeds the cap, a terminal empty chunk is injected to stop
       further reads, keeping peak memory bounded at MAX_BODY_BYTES + one chunk.
       The route handler receives a truncated body and may return a 422; this
       middleware overrides that response with 413 after call_next returns.

    This dual approach closes the chunked-body DoS vector (ID-016) that the
    Content-Length-only check left open.
    """

    MAX_BODY_BYTES = 32 * 1024  # 32 KB — generous for any contact form payload

    async def dispatch(self, request: Request, call_next):
        # ── Fast-path: Content-Length declared ──────────────────────────────
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                if int(content_length) > self.MAX_BODY_BYTES:
                    return JSONResponse(
                        {"detail": "Request body too large."},
                        status_code=413,
                    )
            except ValueError:
                return JSONResponse(
                    {"detail": "Invalid Content-Length header."},
                    status_code=400,
                )

        body_bytes_received: int = 0
        limit_exceeded: bool = False
        original_receive = request._receive

        async def capped_receive() -> dict:
            nonlocal body_bytes_received, limit_exceeded
            message = await original_receive()
            if message.get("type") == "http.request":
                body_bytes_received += len(message.get("body", b""))
                if body_bytes_received > self.MAX_BODY_BYTES:
                    limit_exceeded = True
                    # Terminate the stream — no further chunks will be read.
                    return {"type": "http.request", "body": b"", "more_body": False}
            return message

        request._receive = capped_receive
        response = await call_next(request)

        if limit_exceeded:
            return JSONResponse(
                {"detail": "Request body too large."},
                status_code=413,
            )

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        nonce = secrets.token_hex(16)
        request.state.nonce = nonce

        response = await call_next(request)

        if CURRENT_ENV == "prod":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "fullscreen=(), camera=(), microphone=(), geolocation=(), "
            "interest-cohort=(), browsing-topics=()"
        )

        csp_directives = [
            "default-src 'self';",
            (
                f"script-src 'self' 'nonce-{nonce}' "
                "https://challenges.cloudflare.com "
                "https://static.cloudflareinsights.com "
                "https://umami.stefanovidesott.com;"
            ),
            "style-src 'self' https://cdnjs.cloudflare.com https://fonts.googleapis.com;",
            "font-src 'self' data: https://cdnjs.cloudflare.com https://fonts.gstatic.com;",
            f"img-src 'self' data: {CMS_PUBLIC_ORIGIN};",
            "frame-src 'self' https://challenges.cloudflare.com;",
            (
                "connect-src 'self' "
                "https://cloudflareinsights.com "
                "https://challenges.cloudflare.com "
                "https://umami.stefanovidesott.com;"
            ),
        ]
        response.headers["Content-Security-Policy"] = " ".join(csp_directives)

        return response


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(BodySizeLimitMiddleware)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(public.router)
app.include_router(api.router)

# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    path_parts = request.url.path.split("/")
    lang = path_parts[1] if len(path_parts) > 1 and path_parts[1] in SUPPORTED_LANGS else "en"

    return templates.TemplateResponse(
        request=request,
        name="404.html",
        context={
            "lang": lang,
            "t": translations[lang],
            "current_page": "home",
        },
        status_code=404,
    )
