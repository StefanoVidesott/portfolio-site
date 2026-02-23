<div align="center">
  <h1>Stefano Videsott - Personal Portfolio 🚀</h1>

  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
    <img src="https://img.shields.io/badge/Alembic-5C6BC0?style=for-the-badge&logo=alembic&logoColor=white" alt="Alembic" />
    <img src="https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3" alt="Pytest" />
    <img src="https://img.shields.io/badge/Sentry-362D59?style=for-the-badge&logo=sentry&logoColor=white" alt="Sentry" />
    <img src="https://img.shields.io/badge/Jinja-B41717?style=for-the-badge&logo=jinja&logoColor=white" alt="Jinja2" />
    <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
    <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
    <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" alt="GitHub Actions" />
    <img src="https://img.shields.io/badge/Cloudflare-F38020?style=for-the-badge&logo=cloudflare&logoColor=white" alt="Cloudflare" />
  </p>
</div>

---

Un portfolio personale web dinamico, bilingue e responsivo costruito con **FastAPI** (Python) e **Vanilla JavaScript/CSS**. Progettato per essere veloce, sicuro e architetturalmente scalabile. Utilizza un approccio "ibrido" che unisce file JSON per la localizzazione statica (i18n) e un database SQLite (gestito tramite SQLAlchemy e Alembic) fungendo da **Custom Headless CMS**.

<p align="center">
  <a href="https://www.stefanovidesott.com" target="_blank">
      <img src="https://img.shields.io/badge/🌐_Live_Demo-www.stefanovidesott.com-005571?style=for-the-badge" alt="Portfolio" />
  </a>
</p>

## ✨ Funzionalità Principali

* 🌍 **Architettura Ibrida e Multilingua (IT / EN):** Interfaccia statica tradotta tramite file `.json` standard (i18n) e *Smart Routing* basato sull'header `Accept-Language`.
* 🗄️ **Custom Headless CMS:** Pannello di amministrazione `/admin` protetto da autenticazione con Cookie di Sessione. Permette operazioni CRUD su tutte le entità (Progetti, Esperienze, ecc.). Il sistema genera dinamicamente i form HTML ispezionando i metadati nativi dei modelli SQLAlchemy.
* 🔄 **Database Migrations:** Gestione dello storico del database e aggiornamenti di schema senza perdita di dati grazie all'integrazione di **Alembic**.
* 🛡️ **Sicurezza A+:** Headers HTTP restrittivi (CSP e HSTS), Rate Limiting IP e Cloudflare Turnstile per la protezione dallo spam.
* 🌐 **SEO & Open Graph:** Implementazione di tag Canonical, Open Graph (per LinkedIn/Facebook), Twitter Cards e Dati Strutturati **JSON-LD** per massimizzare la visibilità sui motori di ricerca.
* 📡 **Osservabilità:** Integrazione con **Sentry** per il tracciamento degli errori backend in tempo reale.
* ✅ **Test Automatizzati:** Test suite completa scritta con `pytest` (utilizzando database in-memory per i test) per validare rotte, smart routing e payload API.
* 🚀 **CI/CD Pipeline:** Deployment tramite **GitHub Actions**. Al push su `main`, la pipeline esegue i test, si collega via SSH, minifica CSS/JS, esegue le migrazioni Alembic, aggiorna i container Docker e svuota la cache di Cloudflare tramite API.

## 🛠️ Stack Tecnologico

* **Backend:** Python 3.10, FastAPI, Uvicorn, Jinja2, SQLAlchemy, Alembic, SlowAPI, python-multipart
* **Database:** SQLite (su Docker Volume persistente)
* **Frontend:** HTML5, CSS3 (Custom Grid System), Vanilla JavaScript
* **DevOps & Testing:** Docker, Nginx, GitHub Actions, Pytest
* **Security & Observability:** Sentry, Cloudflare Turnstile, SecurityHeaders Middleware

## 📂 Struttura del Progetto

```text
portfolio-site/
├── .github/workflows/       # Pipeline CI/CD (deploy.yml)
├── alembic/                 # Configurazioni e versioning delle migrazioni DB
├── app/
│   ├── main.py              # Logica API FastAPI, Middleware, Routing Universale
│   ├── database.py          # Configurazione engine SQLAlchemy e sessioni
│   ├── models.py            # Modelli del database con metadati per i form dinamici
│   ├── locales/             # File JSON per le traduzioni statiche dell'UI (it/en)
│   ├── static/              # Asset statici (CSS, JS minificati, immagini, PDF)
│   ├── templates/           # Template HTML (Jinja2), incluse le macro per l'Admin
│   └── tests/               # Suite di test automatizzati (pytest)
├── alembic.ini              # Configurazione base di Alembic
├── seed.py                  # Script Python per popolare il database iniziale
├── .env.example             # Template per le variabili d'ambiente
├── docker-compose.yml       # Configurazione Docker (Produzione)
├── docker-compose.override.yml.dev # Configurazione Docker (Sviluppo locale)
└── Dockerfile               # Istruzioni build dell'immagine Python
```

## 🚀 Come avviare il progetto in locale (Development)

1. **Clona la repository:**

```bash
git clone https://github.com/StefanoVidesott/portfolio-site.git
cd portfolio-site
```

2. **Configura le variabili d'ambiente:**
Crea un file `.env` (o rinomina `.env.example`) nella root del progetto e inserisci le credenziali:

```env
ENVIRONMENT=dev
SECRET_KEY=stringa_casuale_per_le_sessioni_admin

# Credenziali Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password_super_sicura

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SENDER_EMAIL=la_tua_email@gmail.com
SENDER_PASSWORD=la_tua_app_password
RECEIVER_EMAIL=la_tua_email@gmail.com

# Chiavi Cloudflare (Test mode in locale)
TURNSTILE_SITE_KEY=1x00000000000000000000AA
TURNSTILE_SECRET_KEY=1x0000000000000000000000000000000AA

# SENTRY_DSN=
# CLOUDFLARE_WEB_ANALYTICS_TOKEN=
```

3. **Inizializza il Database:**
Assicurati che esista la cartella `data/` nella root. Avvia i container, esegui le migrazioni per creare le tabelle e poi lancia lo script di seeding per popolare i contenuti:

```bash
docker compose up -d --build
docker exec -it portfolio_container alembic upgrade head
docker exec -it portfolio_container python seed.py
```

*Il sito sarà disponibile all'indirizzo `http://localhost:8001`.*

4. **Esegui i Test Automatizzati:**

```bash
docker exec -it portfolio_container python -m pytest
```

## 🚢 Messa in Produzione (Deployment)

Questo progetto sfrutta un approccio **CI/CD automatizzato**.
Ogni `git push` sul ramo `main` innesca una GitHub Action che esegue la suite di test. Solo se i test hanno successo, la pipeline si collega via SSH al server di produzione, minifica gli asset frontend, ricostruisce l'immagine Docker, esegue `alembic upgrade head` per allineare il database e svuota la cache di Cloudflare.

**Per il setup iniziale sul server:**

1. Clona la repository sul server e imposta `ENVIRONMENT=prod` nel file `.env`.
2. Inserisci i token reali di Cloudflare, Sentry e le credenziali SMTP e Admin.
3. La porta esposta da Docker (es. `8001`) è progettata per essere servita tramite un reverse proxy **Nginx** con certificati SSL.
