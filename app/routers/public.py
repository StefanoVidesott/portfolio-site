from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.shared import templates, translations, SUPPORTED_LANGS

router = APIRouter()


@router.get("/favicon.ico")
async def get_favicon():
    return FileResponse("app/static/favicon.ico")


@router.get("/robots.txt")
async def get_robots():
    return FileResponse("app/static/robots.txt")


@router.get("/sitemap.xml")
async def get_sitemap():
    return FileResponse("app/static/sitemap.xml")


@router.get("/")
async def root(request: Request):
    accept_language = request.headers.get("accept-language", "")
    if accept_language.startswith("it"):
        return RedirectResponse(url="/it/home")
    return RedirectResponse(url="/en/home")


@router.get("/{lang}/home")
async def home(request: Request, lang: str, db: Session = Depends(get_db)):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/home")

    db_experiences = (
        db.query(models.Experience)
        .filter(models.Experience.is_featured == True)
        .order_by(models.Experience.order)
        .all()
    )
    db_education = (
        db.query(models.Education)
        .filter(models.Education.is_featured == True)
        .order_by(models.Education.order)
        .all()
    )
    db_skills = (
        db.query(models.SkillCategory)
        .filter(models.SkillCategory.is_featured == True)
        .order_by(models.SkillCategory.order)
        .all()
    )
    db_interests = (
        db.query(models.Interest)
        .filter(models.Interest.is_featured == True)
        .order_by(models.Interest.order)
        .all()
    )
    db_languages = (
        db.query(models.Language)
        .filter(models.Language.is_featured == True)
        .order_by(models.Language.order)
        .all()
    )

    open_to_work = db.query(models.OpenToWork).first()
    cv_doc = db.query(models.CVDocument).filter(models.CVDocument.lang == lang).first()
    cv_url = cv_doc.file_url if cv_doc else None

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "lang": lang,
            "t": translations[lang],
            "experiences": db_experiences,
            "education": db_education,
            "skills": db_skills,
            "interests": db_interests,
            "languages": db_languages,
            "open_to_work": open_to_work,
            "cv_url": cv_url,
            "current_page": "home",
        },
    )


@router.get("/{lang}/projects")
async def projects(request: Request, lang: str, db: Session = Depends(get_db)):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/projects")

    db_projects = (
        db.query(models.Project)
        .filter(models.Project.is_featured == True)
        .order_by(models.Project.order)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={
            "lang": lang,
            "t": translations[lang],
            "projects": db_projects,
            "current_page": "projects",
        },
    )


@router.get("/{lang}/project/wannawork")
async def project_wannawork(request: Request, lang: str):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/project/wannawork")

    return templates.TemplateResponse(
        request=request,
        name="project_wannawork.html",
        context={
            "lang": lang,
            "t": translations[lang],
            "current_page": "project/wannawork",
        },
    )


@router.get("/{lang}/project/portfolio")
async def project_portfolio(request: Request, lang: str):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/project/portfolio")

    return templates.TemplateResponse(
        request=request,
        name="project_portfolio.html",
        context={
            "lang": lang,
            "t": translations[lang],
            "current_page": "project/portfolio",
        },
    )


@router.get("/{lang}/privacy")
async def privacy_policy(request: Request, lang: str):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/it/privacy")

    return templates.TemplateResponse(
        request=request,
        name="privacy.html",
        context={
            "lang": lang,
            "t": translations[lang],
            "current_page": "privacy",
        },
    )
