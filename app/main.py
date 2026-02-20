from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, FileResponse
from app.translations import translations

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

SUPPORTED_LANGS = ["it", "en"]

@app.get("/")
async def root():
    return RedirectResponse(url="/en/home")

@app.get("/{lang}/home")
async def home(request: Request, lang: str):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/home")

    return templates.TemplateResponse("home.html", {
        "request": request,
        "lang": lang,
        "t": translations[lang],
        "current_page": "home"
    })

@app.get("/{lang}/projects")
async def projects(request: Request, lang: str):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/projects")

    return templates.TemplateResponse("projects.html", {
        "request": request,
        "lang": lang,
        "t": translations[lang],
        "current_page": "projects"
    })

@app.get("/{lang}/project/wannawork")
async def project_wannawork(request: Request, lang: str):
    if lang not in SUPPORTED_LANGS:
        return RedirectResponse(url="/en/project/wannawork")

    return templates.TemplateResponse("project_wannawork.html", {
        "request": request,
        "lang": lang,
        "t": translations[lang],
        "current_page": "project/wannawork"
    })

@app.get("/robots.txt")
async def get_robots():
    return FileResponse("app/static/robots.txt")

@app.get("/sitemap.xml")
async def get_sitemap():
    return FileResponse("app/static/sitemap.xml")