<div align="center">
  <h1>Stefano Videsott - Personal Portfolio 🚀</h1>

  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
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

Un portfolio personale web dinamico, bilingue e responsivo costruito con **FastAPI** (Python) e **Vanilla JavaScript/CSS**. Progettato per essere veloce, sicuro e architetturalmente scalabile. Utilizza un approccio "ibrido" che unisce file JSON per la localizzazione statica (i18n) e un database SQLite (gestito tramite SQLAlchemy) per i contenuti dinamici.

<p align="center">
  <a href="https://www.stefanovidesott.com" target="_blank">
      <img src="https://img.shields.io/badge/🌐_Live_Demo-www.stefanovidesott.com-005571?style=for-the-badge" alt="Portfolio" />
  </a>
</p>

## ✨ Funzionalità Principali

* 🌍 **Architettura Ibrida e Multilingua (IT / EN):** Interfaccia statica tradotta tramite file `.json` standard (i18n) e *Smart Routing* basato sull'header `Accept-Language`.
* 🗄️ **Database-Driven (CMS):** Progetti, Esperienze Lavorative, Istruzione, Competenze e Lingue sono entità relazionali salvate su **SQLite** ed estratte dinamicamente tramite **SQLAlchemy**.
* 🛡️ **Sicurezza Avanzata:**  Headers HTTP restrittivi (**CSP** e **HSTS**) implementati via Middleware per proteggere da XSS/Clickjacking. 
  * Integrazione nativa con **Cloudflare Turnstile** per il blocco bot.
  * **Rate Limiting** basato su IP (tramite `slowapi`) per proteggere l'endpoint di contatto dallo spamming.
* 📡 **Osservabilità e Monitoraggio:** Integrazione con **Sentry** per il tracciamento degli errori in tempo reale e il monitoraggio delle performance in produzione.
* 📧 **Form di Contatto Asincrono:** Endpoint API backend che utilizza i `BackgroundTasks` di FastAPI e `smtplib` per inviare e-mail reali senza bloccare il thread principale o la UI.
* ✅ **Test Automatizzati:** Test suite completa scritta con `pytest` per validare rotte, smart routing, gestione 404 e validazione dei payload API.
* 🚀 **CI/CD Pipeline:** Deployment tramite **GitHub Actions**. Al push su `main`, la pipeline esegue i test, si collega via SSH, minifica CSS e JS, aggiorna i container Docker e svuota la cache di Cloudflare tramite API.

## 🛠️ Stack Tecnologico

* **Backend:** Python 3.10, FastAPI, Uvicorn, Jinja2, SQLAlchemy, SlowAPI
* **Database:** SQLite (su Docker Volume persistente)
* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **DevOps & Testing:** Docker, Nginx, GitHub Actions, Pytest
* **Security & Observability:** Sentry, Cloudflare Turnstile, Web Analytics

## 📂 Struttura del Progetto

```text
portfolio-site/
├── .github/workflows/       # Pipeline CI/CD (deploy.yml)
├── app/
│   ├── main.py              # Logica API FastAPI, Middleware, Rate Limiting
│   ├── database.py          # Configurazione engine SQLAlchemy e sessioni
│   ├── models.py            # Modelli del database (Project, Experience, ecc.)
│   ├── locales/             # File JSON per le traduzioni statiche dell'UI (it/en)
│   ├── static/              # Asset statici (CSS, JS minificati, immagini, PDF)
│   ├── templates/           # Template HTML (Jinja2)
│   └── tests/               # Suite di test automatizzati (pytest)
├── seed.py                  # Script Python per inizializzare e popolare il database
├── .env.example             # Template per le variabili d'ambiente
├── docker-compose.yml       # Configurazione Docker (Produzione)
├── docker-compose.override.yml.dev # Configurazione Docker (Sviluppo locale)
├── Dockerfile               # Istruzioni build dell'immagine Python
└── requirements.txt         # Dipendenze Python
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

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SENDER_EMAIL=la_tua_email@gmail.com
SENDER_PASSWORD=la_tua_app_password
RECEIVER_EMAIL=la_tua_email@gmail.com

# Chiavi di test (Always Pass) per lo sviluppo locale
TURNSTILE_SITE_KEY=1x00000000000000000000AA
TURNSTILE_SECRET_KEY=1x0000000000000000000000000000000AA

SENTRY_DSN= # (lasciare vuoto in locale per disabilitare il tracciamento)
CLOUDFLARE_WEB_ANALYTICS_TOKEN= # (lasciare vuoto in locale)
```

3. **Inizializza il Database:**
Assicurati che esista la cartella `data/` nella root. Avvia i container e poi lancia lo script di seeding per popolare i contenuti:

```bash
docker compose up -d --build
docker exec -it portfolio_container python seed.py
```

*Il sito sarà disponibile all'indirizzo `http://localhost:8001`.*

4. **Esegui i Test Automatizzati:**

```bash
docker exec -it portfolio_container python -m pytest
```

## 🚢 Messa in Produzione (Deployment)

Questo progetto sfrutta un approccio **CI/CD automatizzato**.
Ogni `git push` sul ramo `main` innesca una GitHub Action che esegue la suite di test. Solo se i test hanno successo, la pipeline si collega via SSH al server di produzione, minifica gli asset frontend, ricostruisce l'immagine Docker e svuota la cache di Cloudflare.

**Per il setup iniziale sul server:**

1. Clona la repository sul server e imposta `ENVIRONMENT=prod` nel file `.env`.
2. Inserisci i token reali di Cloudflare, Sentry e le credenziali SMTP.
3. Esegui il seed iniziale del database.
4. La porta esposta da Docker (es. `8001`) è progettata per essere servita tramite un reverse proxy **Nginx** con certificati SSL.
