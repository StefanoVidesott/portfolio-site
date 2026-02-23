import os
import json
import httpx
import secrets
import smtplib
import sentry_sdk

from app import models
from app.database import engine, Base, get_db

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from email.message import EmailMessage
from dotenv import load_dotenv
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sqlalchemy.orm import Session

load_dotenv()

SUPPORTED_LANGS = ["it", "en"]
CURRENT_ENV = os.getenv("ENVIRONMENT", "dev")
TURNSTILE_SITE_KEY = os.getenv("TURNSTILE_SITE_KEY", "")
TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY", "")
CLOUDFLARE_WEB_ANALYTICS_TOKEN = os.getenv("CLOUDFLARE_WEB_ANALYTICS_TOKEN", "")
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
ENTITY_MODELS = {
    "projects": models.Project,
    "skills": models.SkillCategory,
    "experiences": models.Experience,
    "education": models.Education,
    "interests": models.Interest,
    "languages": models.Language,
}

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

translations = {}
locales_dir = os.path.join(os.path.dirname(__file__), "locales")

for lang in SUPPORTED_LANGS:
    file_path = os.path.join(locales_dir, f"{lang}.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            translations[lang] = json.load(f)
    except FileNotFoundError:
        print(f"ATTENZIONE: File di traduzione non trovato per la lingua: {lang}")
        translations[lang] = {}

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["env"] = CURRENT_ENV
templates.env.globals["turnstile_site_key"] = TURNSTILE_SITE_KEY
templates.env.globals["cloudflare_web_analytics_token"] = CLOUDFLARE_WEB_ANALYTICS_TOKEN

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        nonce = secrets.token_hex(16)
        request.state.nonce = nonce

        response = await call_next(request)

        if os.getenv("ENVIRONMENT") == "prod":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "fullscreen=(), camera=(), microphone=(), geolocation=(), interest-cohort=(), browsing-topics=()"

        csp_directives = [
            "default-src 'self';",
            f"script-src 'self' 'nonce-{nonce}' https://challenges.cloudflare.com https://static.cloudflareinsights.com;",
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com;",
            "font-src 'self' data: https://cdnjs.cloudflare.com https://fonts.gstatic.com;",
            "img-src 'self' data:;",
            "frame-src 'self' https://challenges.cloudflare.com;",
            "connect-src 'self' https://cloudflareinsights.com https://challenges.cloudflare.com;"
        ]
        response.headers["Content-Security-Policy"] = " ".join(csp_directives)

        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "chiave-di-sviluppo-fallback"))

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

def generate_form_schema(model_class, instance=None):
    schema = {}

    for column in model_class.__table__.columns:
        if column.name == "id":
            continue

        info = column.info or {}
        group_name = info.get("group", "Altro")

        if group_name not in schema:
            schema[group_name] = []

        val = ""
        if instance and hasattr(instance, column.name):
            val = getattr(instance, column.name)
            if val is None: val = ""
        elif column.default is not None:
            val = column.default.arg if not callable(column.default.arg) else ""

        schema[group_name].append({
            "name": column.name,
            "type": info.get("type", "text"),
            "required": not column.nullable,
            "value": val,
            "size": info.get("size", "12" if info.get("type") == "textarea" else "6")
        })

    return schema

def populate_instance_from_form(instance, model_class, form_data):
    for column in model_class.__table__.columns:
        if column.name == "id":
            continue

        if getattr(column.type, "python_type", None) is bool or str(column.type) == "BOOLEAN":
            val = form_data.get(column.name)
            setattr(instance, column.name, val in ["true", "on", "1"])
            continue

        if str(column.type) == "JSON":
            val = form_data.get(column.name, "")
            if val:
                lines = [line.strip() for line in val.split("\n") if line.strip()]
                setattr(instance, column.name, lines)
            else:
                setattr(instance, column.name, [])
            continue

        if column.name in form_data:
            val = form_data.get(column.name)
            if val == "":
                if column.nullable:
                    setattr(instance, column.name, None)
                elif getattr(column.type, "python_type", None) is int:
                    setattr(instance, column.name, 0)
                else:
                    setattr(instance, column.name, "")
            else:
                setattr(instance, column.name, val)

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
async def home(request: Request, lang: str, db: Session = Depends(get_db)):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/home")

    db_experiences = db.query(models.Experience).filter(models.Experience.is_featured == True).order_by(models.Experience.order).all()
    db_education = db.query(models.Education).filter(models.Education.is_featured == True).order_by(models.Education.order).all()
    db_skills = db.query(models.SkillCategory).filter(models.SkillCategory.is_featured == True).order_by(models.SkillCategory.order).all()
    db_interests = db.query(models.Interest).filter(models.Interest.is_featured == True).order_by(models.Interest.order).all()
    db_languages = db.query(models.Language).filter(models.Language.is_featured == True).order_by(models.Language.order).all()

    return templates.TemplateResponse(request=request, name="home.html", context={
        "lang": lang,
        "t": translations[lang],
        "experiences": db_experiences,
        "education": db_education,
        "skills": db_skills,
        "interests": db_interests,
        "languages": db_languages,
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
async def projects(request: Request, lang: str, db: Session = Depends(get_db)):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/projects")

    db_projects = db.query(models.Project).filter(models.Project.is_featured == True).order_by(models.Project.order).all()

    return templates.TemplateResponse(request=request, name="projects.html", context={
        "lang": lang,
        "t": translations[lang],
        "projects": db_projects,
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

@app.get("/admin")
async def admin_redirect(request: Request):
    accept_language = request.headers.get("accept-language", "")

    if accept_language.startswith("it"):
        return RedirectResponse(url="/it/admin/login")

    return RedirectResponse(url="/en/admin/login")

@app.get("/{lang}/admin/login")
async def admin_login_page(request: Request, lang: str):

    if request.session.get("is_admin"):
        return RedirectResponse(url=f"/{lang}/admin/dashboard")

    return templates.TemplateResponse(request=request, name="login.html", context={
        "lang": lang,
        "t": translations[lang],
        "current_page": f"/{lang}/admin/login"
    })

@app.post("/{lang}/admin/login")
async def admin_login(
    request: Request,
    lang: str,
    username: str = Form(...),
    password: str = Form(...)
):
    correct_username = os.getenv("ADMIN_USERNAME")
    correct_password = os.getenv("ADMIN_PASSWORD")

    if username == correct_username and password == correct_password:
        request.session["is_admin"] = True
        return RedirectResponse(url=f"/{lang}/admin/dashboard", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": translations[lang]['admin']['login']['error_invalid'],
            "lang": lang,
            "t": translations[lang],
            "current_page": "admin/login"
        },
        status_code=401
    )

@app.get("/{lang}/admin/logout")
async def admin_logout(request: Request, lang: str):
    request.session.clear()
    return RedirectResponse(url=f"/{lang}/home")

@app.get("/{lang}/admin/dashboard")
async def admin_dashboard(request: Request, lang: str, db: Session = Depends(get_db)):
    if not request.session.get("is_admin"):
        return RedirectResponse(url=f"/{lang}/admin/login")

    db_projects = db.query(models.Project).order_by(models.Project.order).all()
    db_skills = db.query(models.SkillCategory).order_by(models.SkillCategory.order).all()
    db_experiences = db.query(models.Experience).order_by(models.Experience.order).all()
    db_education = db.query(models.Education).order_by(models.Education.order).all()
    db_interests = db.query(models.Interest).order_by(models.Interest.order).all()
    db_languages = db.query(models.Language).order_by(models.Language.order).all()

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "projects": db_projects,
            "skills": db_skills,
            "experiences": db_experiences,
            "education": db_education,
            "interests": db_interests,
            "languages": db_languages,
            "lang": lang,
            "t": translations[lang],
            "current_page": "admin/dashboard"
        })

@app.get("/{lang}/admin/{entity_type}/new")
async def new_entity_page(request: Request, lang: str, entity_type: str):
    if not request.session.get("is_admin"):
        return RedirectResponse(url=f"/{lang}/admin/login")

    model_class = ENTITY_MODELS.get(entity_type)
    if not model_class:
        return RedirectResponse(url=f"/{lang}/admin/dashboard")

    form_schema = generate_form_schema(model_class)

    return templates.TemplateResponse(
        request=request,
        name="admin_dynamic_form.html",
        context={
            "lang": lang,
            "t": translations[lang],
            "schema": form_schema,
            "action_url": f"/admin/{entity_type}/new",
            "title": f"{translations['it']['admin']['forms']['actions']['new_prefix']} {entity_type.capitalize()}",
            "current_page": f"admin/{entity_type}/new"
        }
    )

@app.post("/admin/{entity_type}/new")
async def create_entity(request: Request, entity_type: str, db: Session = Depends(get_db)):
    if not request.session.get("is_admin"):
        return RedirectResponse(url=f"/{lang}/admin/login")

    model_class = ENTITY_MODELS.get(entity_type)
    if not model_class:
        return RedirectResponse(url=f"/{lang}/admin/dashboard")

    form_data = await request.form()

    new_item = model_class()
    populate_instance_from_form(new_item, model_class, form_data)

    db.add(new_item)
    db.commit()

    return RedirectResponse(url=f"/{lang}/admin/dashboard", status_code=303)


@app.get("/{lang}/admin/{entity_type}/edit/{item_id}")
async def edit_entity_page(request: Request, lang: str, entity_type: str, item_id: int, db: Session = Depends(get_db)):
    if not request.session.get("is_admin"):
        return RedirectResponse(url=f"/{lang}/admin/login")

    model_class = ENTITY_MODELS.get(entity_type)
    if not model_class:
        return RedirectResponse(url=f"/{lang}/admin/dashboard")

    item = db.query(model_class).filter(model_class.id == item_id).first()
    if not item:
        return RedirectResponse(url=f"/{lang}/admin/dashboard")

    for col in model_class.__table__.columns:
        if str(col.type) == "JSON":
            current_val = getattr(item, col.name)
            if isinstance(current_val, list):
                setattr(item, col.name, "\n".join(current_val))

    form_schema = generate_form_schema(model_class, instance=item)

    display_title = getattr(item, 'title_it', getattr(item, 'name', f"ID {item.id}"))

    return templates.TemplateResponse(
        request=request,
        name="admin_dynamic_form.html",
        context={
            "lang": lang,
            "t": translations[lang],
            "schema": form_schema,
            "action_url": f"/admin/{entity_type}/edit/{item.id}",
            "title": f"{translations['it']['admin']['forms']['actions']['edit_prefix']} {display_title}",
            "current_page": f"admin/{entity_type}/edit/{item_id}"
        }
    )

@app.post("/admin/{entity_type}/edit/{item_id}")
async def update_entity(request: Request, entity_type: str, item_id: int, db: Session = Depends(get_db)):
    if not request.session.get("is_admin"):
        return RedirectResponse(url=f"/{lang}/admin/login")

    model_class = ENTITY_MODELS.get(entity_type)
    if not model_class:
        return RedirectResponse(url=f"/{lang}/admin/dashboard")

    db_item = db.query(model_class).filter(model_class.id == item_id).first()
    if not db_item:
         return RedirectResponse(url=f"/{lang}/admin/dashboard")

    form_data = await request.form()
    populate_instance_from_form(db_item, model_class, form_data)

    db.commit()
    return RedirectResponse(url=f"/{lang}/admin/dashboard", status_code=303)


@app.post("/admin/{entity_type}/delete/{item_id}")
async def delete_entity(request: Request, entity_type: str, item_id: int, db: Session = Depends(get_db)):
    if not request.session.get("is_admin"):
        return RedirectResponse(url=f"/{lang}/admin/login")

    model_class = ENTITY_MODELS.get(entity_type)
    if model_class:
        db_item = db.query(model_class).filter(model_class.id == item_id).first()
        if db_item:
            db.delete(db_item)
            db.commit()

    return RedirectResponse(url=f"/{lang}/admin/dashboard", status_code=303)

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
