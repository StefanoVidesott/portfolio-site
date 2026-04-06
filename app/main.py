import os
import secrets
from contextlib import asynccontextmanager

import httpx
import sentry_sdk

from fastapi import FastAPI, Request
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
# Public origin used by the *browser* to load static assets (images, etc.).
# Must differ from CMS_API_BASE_URL in Docker dev: the browser cannot resolve
# host.docker.internal, so we need the host-accessible address here.
CMS_PUBLIC_ORIGIN = os.getenv("CMS_PUBLIC_ORIGIN", "http://localhost:8004")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        enable_tracing=True,
        traces_sample_rate=1.0,
        environment=CURRENT_ENV,
        integrations=[
            StarletteIntegration(transaction_style="url"),
            FastApiIntegration(transaction_style="url"),
        ],
    )

# ---------------------------------------------------------------------------
# Lifespan — manages the shared httpx client
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create one shared AsyncClient for the process lifetime.

    Re-using a single client is more efficient than opening a new TCP connection
    on every incoming request (connection pooling, keep-alive, DNS caching).
    """
    app.state.http_client = httpx.AsyncClient()
    app.state.cms_base_url = CMS_API_BASE_URL
    app.state.cms_public_origin = CMS_PUBLIC_ORIGIN
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
