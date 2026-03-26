import os
import secrets

import sentry_sdk

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from app.shared import templates, translations, SUPPORTED_LANGS
from app.routers import public, admin, api
from app.cms import UPLOAD_DIR, PDF_UPLOAD_DIR

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CURRENT_ENV = os.getenv("ENVIRONMENT", "dev")
TURNSTILE_SITE_KEY = os.getenv("TURNSTILE_SITE_KEY", "")
CLOUDFLARE_WEB_ANALYTICS_TOKEN = os.getenv("CLOUDFLARE_WEB_ANALYTICS_TOKEN", "")
SENTRY_DSN = os.getenv("SENTRY_DSN", "")

_secret_key = os.getenv("SECRET_KEY")
if not _secret_key:
    if CURRENT_ENV == "prod":
        raise RuntimeError(
            "SECRET_KEY environment variable must be set in production. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    # Dev-only fallback — never used in prod
    _secret_key = "dev-only-insecure-fallback-do-not-use-in-production"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)

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
# App & static files
# ---------------------------------------------------------------------------
app = FastAPI()
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
            # No 'unsafe-inline' — all inline styles have been moved to CSS classes
            "style-src 'self' https://cdnjs.cloudflare.com https://fonts.googleapis.com;",
            "font-src 'self' data: https://cdnjs.cloudflare.com https://fonts.gstatic.com;",
            "img-src 'self' data:;",
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
app.add_middleware(SessionMiddleware, secret_key=_secret_key)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(public.router)
app.include_router(admin.router)
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
