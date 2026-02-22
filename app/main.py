import os
import httpx
import smtplib
import sentry_sdk

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from email.message import EmailMessage
from dotenv import load_dotenv
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from app.translations import translations

load_dotenv()

SUPPORTED_LANGS = ["it", "en"]
CURRENT_ENV = os.getenv("ENVIRONMENT", "dev")
TURNSTILE_SITE_KEY = os.getenv("TURNSTILE_SITE_KEY", "")
TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY", "")
CLOUDFLARE_WEB_ANALYTICS_TOKEN = os.getenv("CLOUDFLARE_WEB_ANALYTICS_TOKEN", "")
SENTRY_DSN = os.getenv("SENTRY_DSN", "")

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

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["env"] = CURRENT_ENV
templates.env.globals["turnstile_site_key"] = TURNSTILE_SITE_KEY
templates.env.globals["cloudflare_web_analytics_token"] = CLOUDFLARE_WEB_ANALYTICS_TOKEN

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if os.getenv("ENVIRONMENT") == "prod":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        csp_directives = [
            "default-src 'self';",
            "script-src 'self' 'unsafe-inline' https://challenges.cloudflare.com https://static.cloudflareinsights.com;",
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com;",
            "font-src 'self' data: https://cdnjs.cloudflare.com https://fonts.gstatic.com;",
            "img-src 'self' data:;",
            "frame-src 'self' https://challenges.cloudflare.com;",
            "connect-src 'self' https://cloudflareinsights.com https://challenges.cloudflare.com;"
        ]
        response.headers["Content-Security-Policy"] = " ".join(csp_directives)

        return response

app.add_middleware(SecurityHeadersMiddleware)

class ContactRequest(BaseModel):
    name: str
    email: str
    message: str
    turnstile_token: str

def send_email_task(contact: ContactRequest):
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
    RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

    msg = EmailMessage()
    msg.set_content(f"Nuovo messaggio dal tuo Portfolio!\n\nNome: {contact.name}\nEmail: {contact.email}\n\nMessaggio:\n{contact.message}")

    msg['Subject'] = f"Nuovo Contatto da: {contact.name}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Errore invio email: {e}")

@app.get("/favicon.ico")
async def get_favicon():
    return FileResponse("app/static/favicon.ico")

@app.get("/")
async def root(request: Request):
    accept_language = request.headers.get("accept-language", "")

    if accept_language.startswith("it"):
        return RedirectResponse(url="/it/home")

    return RedirectResponse(url="/en/home")

@app.get("/{lang}/home")
async def home(request: Request, lang: str):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/home")

    return templates.TemplateResponse(request=request, name="home.html", context={
        "lang": lang,
        "t": translations[lang],
        "current_page": "home"
    })

@app.post("/api/contact")
async def handle_contact(contact: ContactRequest, background_tasks: BackgroundTasks):
    if TURNSTILE_SECRET_KEY:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={
                    "secret": TURNSTILE_SECRET_KEY,
                    "response": contact.turnstile_token
                }
            )
            result = response.json()

            if not result.get("success"):
                raise HTTPException(status_code=400, detail="Controllo anti-spam fallito.")

    background_tasks.add_task(send_email_task, contact)
    return {"status": "success", "message": "Email is being sent"}

@app.get("/{lang}/projects")
async def projects(request: Request, lang: str):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/projects")

    return templates.TemplateResponse(request=request, name="projects.html", context={
        "lang": lang,
        "t": translations[lang],
        "current_page": "projects"
    })

@app.get("/{lang}/project/wannawork")
async def project_wannawork(request: Request, lang: str):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/project/wannawork")

    return templates.TemplateResponse(request=request, name="project_wannawork.html", context={
        "lang": lang,
        "t": translations[lang],
        "current_page": "project/wannawork"
    })

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    path_parts = request.url.path.split('/')
    lang = path_parts[1] if len(path_parts) > 1 and path_parts[1] in SUPPORTED_LANGS else "en"

    return templates.TemplateResponse(request=request, name="404.html", context={
        "lang": lang,
        "t": translations[lang],
        "current_page": "home"
    }, status_code=404)

@app.get("/robots.txt")
async def get_robots():
    return FileResponse("app/static/robots.txt")

@app.get("/sitemap.xml")
async def get_sitemap():
    return FileResponse("app/static/sitemap.xml")
