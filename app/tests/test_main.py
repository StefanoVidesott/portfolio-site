import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
def test_homepage_english():
    """Verifica che la homepage in inglese si carichi correttamente (Status 200)"""
    response = client.get("/en/home")
    assert response.status_code == 200
    assert b"Stefano Videsott" in response.content
    assert b"Software Developer" in response.content

def test_homepage_italian():
    """Verifica che la homepage in italiano si carichi correttamente (Status 200)"""
    response = client.get("/it/home")
    assert response.status_code == 200
    assert b"Stefano Videsott" in response.content
    assert b"Sviluppatore Software" in response.content

def test_smart_routing():
    """Verifica che la root (/) reindirizzi correttamente in base all'Accept-Language"""
    response = client.get("/", headers={"Accept-Language": "it-IT,it;q=0.9"})
    assert response.status_code == 200
    assert str(response.url).endswith("/it/home")

def test_contact_form_validation():
    """Verifica che il form API blocchi le richieste incomplete (Status 422 - Unprocessable Entity)"""
    incomplete_payload = {
        "name": "Test User",
    }
    response = client.post("/api/contact", json=incomplete_payload)
    assert response.status_code == 422

def test_unsupported_language_redirect():
    """Verifica che una lingua non supportata (es. 'fr') reindirizzi all'inglese"""
    response = client.get("/fr/home", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/en/home"

def test_projects_page():
    """Verifica che la pagina progetti si carichi correttamente"""
    response = client.get("/en/projects")
    assert response.status_code == 200
    assert b"Projects" in response.content

def test_wannawork_detail_page():
    """Verifica che la pagina di dettaglio di WannaWork si carichi"""
    response = client.get("/it/project/wannawork")
    assert response.status_code == 200
    assert b"WannaWork" in response.content

def test_404_not_found():
    """Verifica che un URL inesistente restituisca la pagina 404 personalizzata"""
    response = client.get("/en/pagina-che-non-esiste")
    assert response.status_code == 404
    assert b"404" in response.content

def test_static_files_exist():
    """Verifica che i file vitali per la SEO siano serviti correttamente"""
    response_robots = client.get("/robots.txt")
    assert response_robots.status_code == 200
    assert b"User-agent" in response_robots.content

    response_sitemap = client.get("/sitemap.xml")
    assert response_sitemap.status_code == 200
    assert b"xml" in response_sitemap.content
