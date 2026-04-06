import asyncio

import httpx

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, FileResponse

from app.shared import templates, translations, SUPPORTED_LANGS

router = APIRouter()


async def _fetch(client: httpx.AsyncClient, url: str) -> list | dict:
    """GET a CMS endpoint; return parsed JSON or [] on any error."""
    try:
        response = await client.get(url, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"CMS fetch error [{url}]: {e}")
        return []


# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------

@router.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    return FileResponse("app/static/favicon.ico")


@router.get("/robots.txt", include_in_schema=False)
async def get_robots():
    return FileResponse("app/static/robots.txt")


@router.get("/sitemap.xml", include_in_schema=False)
async def get_sitemap():
    return FileResponse("app/static/sitemap.xml")


@router.get("/", include_in_schema=False)
async def root(request: Request):
    accept_language = request.headers.get("accept-language", "")
    lang = "it" if accept_language.startswith("it") else "en"
    return RedirectResponse(url=f"/{lang}/home")


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

@router.get("/{lang}/home")
async def home(request: Request, lang: str):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/home")

    client: httpx.AsyncClient = request.app.state.http_client
    base = request.app.state.cms_base_url

    (
        api_experiences, api_education, api_skills, api_interests,
        api_languages, api_otw, api_cvs,
    ) = await asyncio.gather(
        _fetch(client, f"{base}/api/public/experiences?lang={lang}"),
        _fetch(client, f"{base}/api/public/educations?lang={lang}"),
        _fetch(client, f"{base}/api/public/skill-categories?lang={lang}"),
        _fetch(client, f"{base}/api/public/interests?lang={lang}"),
        _fetch(client, f"{base}/api/public/languages?lang={lang}"),
        _fetch(client, f"{base}/api/public/open-to-work?lang={lang}"),
        _fetch(client, f"{base}/api/public/cv-documents?lang={lang}"),
    )

    # Show the download button only when the ERP has a CV for this language.
    # The href points to the ERP's dedicated download endpoint so the browser
    # receives a proper Content-Disposition header with a clean filename.
    cv_exists = any(cv.get("lang") == lang for cv in (api_cvs or []))
    cms_public = request.app.state.cms_public_origin
    cv_url = f"{cms_public}/api/public/download-cv?lang={lang}" if cv_exists else None

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "lang": lang,
            "t": translations[lang],
            "experiences": [x for x in (api_experiences or []) if x.get("is_featured")],
            "education": [x for x in (api_education or []) if x.get("is_featured")],
            "skills": [x for x in (api_skills or []) if x.get("is_featured")],
            "interests": [x for x in (api_interests or []) if x.get("is_featured")],
            "languages": [x for x in (api_languages or []) if x.get("is_featured")],
            "open_to_work": (api_otw or [None])[0],
            "cv_url": cv_url,
            "current_page": "home",
        },
    )


@router.get("/{lang}/projects")
async def projects(request: Request, lang: str):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/projects")

    client: httpx.AsyncClient = request.app.state.http_client
    base = request.app.state.cms_base_url

    api_projects = await _fetch(client, f"{base}/api/public/projects?lang={lang}")

    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={
            "lang": lang,
            "t": translations[lang],
            "projects": api_projects or [],
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
