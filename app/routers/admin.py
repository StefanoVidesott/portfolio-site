import hmac
import secrets

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.cms import generate_form_schema, populate_instance_from_form, UPLOAD_DIR
from app.shared import templates, translations, SUPPORTED_LANGS

import os

router = APIRouter()

ENTITY_MODELS = {
    "projects": models.Project,
    "skills": models.SkillCategory,
    "experiences": models.Experience,
    "education": models.Education,
    "interests": models.Interest,
    "languages": models.Language,
}

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")


def _require_admin(request: Request, lang: str):
    """Return a redirect if the session has no valid admin flag, else None."""
    if not request.session.get("is_admin"):
        return RedirectResponse(url=f"/{lang}/admin/login")
    return None


def _validate_csrf(request_session: dict, form_csrf: str):
    """Raise 403 if the submitted CSRF token doesn't match the session token."""
    session_token = request_session.get("csrf_token", "")
    if not hmac.compare_digest(session_token, form_csrf or ""):
        raise HTTPException(status_code=403, detail="Invalid CSRF token.")


def _ensure_csrf(request: Request) -> str:
    """Return the session CSRF token, generating one if absent."""
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_hex(32)
    return request.session["csrf_token"]


# ---------------------------------------------------------------------------
# Login / Logout
# ---------------------------------------------------------------------------

@router.get("/admin")
async def admin_redirect(request: Request):
    accept_language = request.headers.get("accept-language", "")
    if accept_language.startswith("it"):
        return RedirectResponse(url="/it/admin/login")
    return RedirectResponse(url="/en/admin/login")


@router.get("/{lang}/admin/login")
async def admin_login_page(request: Request, lang: str):
    if lang not in SUPPORTED_LANGS:
        lang = "en"

    if request.session.get("is_admin"):
        return RedirectResponse(url=f"/{lang}/admin/dashboard")

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "lang": lang,
            "t": translations[lang],
            "current_page": f"/{lang}/admin/login",
        },
    )


@router.post("/{lang}/admin/login")
async def admin_login(
    request: Request,
    lang: str,
    username: str = Form(...),
    password: str = Form(...),
):
    if lang not in SUPPORTED_LANGS:
        lang = "en"

    # Constant-time comparison to prevent timing attacks
    username_ok = hmac.compare_digest(username or "", ADMIN_USERNAME)
    password_ok = hmac.compare_digest(password or "", ADMIN_PASSWORD)

    if username_ok and password_ok:
        request.session["is_admin"] = True
        # Mint a fresh CSRF token on every successful login
        request.session["csrf_token"] = secrets.token_hex(32)
        return RedirectResponse(url=f"/{lang}/admin/dashboard", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": translations[lang]["admin"]["login"]["error_invalid"],
            "lang": lang,
            "t": translations[lang],
            "current_page": "admin/login",
        },
        status_code=401,
    )


@router.get("/{lang}/admin/logout")
async def admin_logout(request: Request, lang: str):
    request.session.clear()
    return RedirectResponse(url=f"/{lang}/home")


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@router.get("/{lang}/admin/dashboard")
async def admin_dashboard(request: Request, lang: str, db: Session = Depends(get_db)):
    if lang not in SUPPORTED_LANGS:
        lang = "en"
    if guard := _require_admin(request, lang):
        return guard

    csrf_token = _ensure_csrf(request)

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
            "current_page": "admin/dashboard",
            "csrf_token": csrf_token,
        },
    )


# ---------------------------------------------------------------------------
# Create entity
# ---------------------------------------------------------------------------

@router.get("/{lang}/admin/{entity_type}/new")
async def new_entity_page(request: Request, lang: str, entity_type: str):
    if lang not in SUPPORTED_LANGS:
        lang = "en"
    if guard := _require_admin(request, lang):
        return guard

    model_class = ENTITY_MODELS.get(entity_type)
    if not model_class:
        return RedirectResponse(url=f"/{lang}/admin/dashboard")

    csrf_token = _ensure_csrf(request)
    form_schema = generate_form_schema(model_class)

    return templates.TemplateResponse(
        request=request,
        name="admin_dynamic_form.html",
        context={
            "lang": lang,
            "t": translations[lang],
            "schema": form_schema,
            "action_url": f"/{lang}/admin/{entity_type}/new",
            "title": f"{translations[lang]['admin']['forms']['actions']['new_prefix']} {entity_type.capitalize()}",
            "current_page": f"admin/{entity_type}/new",
            "csrf_token": csrf_token,
        },
    )


@router.post("/{lang}/admin/{entity_type}/new")
async def create_entity(
    request: Request, lang: str, entity_type: str, db: Session = Depends(get_db)
):
    if lang not in SUPPORTED_LANGS:
        lang = "en"
    if guard := _require_admin(request, lang):
        return guard

    model_class = ENTITY_MODELS.get(entity_type)
    if not model_class:
        return RedirectResponse(url=f"/{lang}/admin/dashboard")

    form_data = await request.form()
    _validate_csrf(request.session, form_data.get("csrf_token", ""))

    new_item = model_class()
    populate_instance_from_form(new_item, model_class, form_data)

    db.add(new_item)
    db.commit()

    return RedirectResponse(url=f"/{lang}/admin/dashboard", status_code=303)


# ---------------------------------------------------------------------------
# Edit entity
# ---------------------------------------------------------------------------

@router.get("/{lang}/admin/{entity_type}/edit/{item_id}")
async def edit_entity_page(
    request: Request,
    lang: str,
    entity_type: str,
    item_id: int,
    db: Session = Depends(get_db),
):
    if lang not in SUPPORTED_LANGS:
        lang = "en"
    if guard := _require_admin(request, lang):
        return guard

    model_class = ENTITY_MODELS.get(entity_type)
    if not model_class:
        return RedirectResponse(url=f"/{lang}/admin/dashboard")

    item = db.query(model_class).filter(model_class.id == item_id).first()
    if not item:
        return RedirectResponse(url=f"/{lang}/admin/dashboard")

    # Convert JSON columns from list → newline-separated string for the textarea
    for col in model_class.__table__.columns:
        if str(col.type) == "JSON":
            current_val = getattr(item, col.name)
            if isinstance(current_val, list):
                setattr(item, col.name, "\n".join(current_val))

    csrf_token = _ensure_csrf(request)
    form_schema = generate_form_schema(model_class, instance=item)
    display_title = getattr(item, "title_it", getattr(item, "name", f"ID {item.id}"))

    return templates.TemplateResponse(
        request=request,
        name="admin_dynamic_form.html",
        context={
            "lang": lang,
            "t": translations[lang],
            "schema": form_schema,
            "action_url": f"/{lang}/admin/{entity_type}/edit/{item.id}",
            "title": f"{translations[lang]['admin']['forms']['actions']['edit_prefix']} {display_title}",
            "current_page": f"admin/{entity_type}/edit/{item_id}",
            "csrf_token": csrf_token,
        },
    )


@router.post("/{lang}/admin/{entity_type}/edit/{item_id}")
async def update_entity(
    request: Request,
    lang: str,
    entity_type: str,
    item_id: int,
    db: Session = Depends(get_db),
):
    if lang not in SUPPORTED_LANGS:
        lang = "en"
    if guard := _require_admin(request, lang):
        return guard

    model_class = ENTITY_MODELS.get(entity_type)
    if not model_class:
        return RedirectResponse(url=f"/{lang}/admin/dashboard")

    db_item = db.query(model_class).filter(model_class.id == item_id).first()
    if not db_item:
        return RedirectResponse(url=f"/{lang}/admin/dashboard")

    form_data = await request.form()
    _validate_csrf(request.session, form_data.get("csrf_token", ""))

    populate_instance_from_form(db_item, model_class, form_data)
    db.commit()

    return RedirectResponse(url=f"/{lang}/admin/dashboard", status_code=303)


# ---------------------------------------------------------------------------
# Delete entity
# ---------------------------------------------------------------------------

@router.post("/{lang}/admin/{entity_type}/delete/{item_id}")
async def delete_entity(
    request: Request,
    lang: str,
    entity_type: str,
    item_id: int,
    db: Session = Depends(get_db),
):
    if lang not in SUPPORTED_LANGS:
        lang = "en"
    if guard := _require_admin(request, lang):
        return guard

    form_data = await request.form()
    _validate_csrf(request.session, form_data.get("csrf_token", ""))

    model_class = ENTITY_MODELS.get(entity_type)
    if model_class:
        db_item = db.query(model_class).filter(model_class.id == item_id).first()
        if db_item:
            # Clean up uploaded image file if present
            image_url = getattr(db_item, "image_url", None)
            if image_url and str(image_url).startswith("/static/images/uploaded/"):
                file_path = os.path.join("app", image_url.lstrip("/"))
                if os.path.isfile(file_path):
                    os.remove(file_path)

            db.delete(db_item)
            db.commit()

    return RedirectResponse(url=f"/{lang}/admin/dashboard", status_code=303)
