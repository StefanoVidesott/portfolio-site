<div align="center">
  <h1>Stefano Videsott - Personal Portfolio 🚀</h1>

  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3" alt="Pytest" />
    <img src="https://img.shields.io/badge/Jinja-B41717?style=for-the-badge&logo=jinja&logoColor=white" alt="Jinja2" />
    <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
    <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
    <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3" />
    <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
    <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" alt="GitHub Actions" />
    <img src="https://img.shields.io/badge/Cloudflare-F38020?style=for-the-badge&logo=cloudflare&logoColor=white" alt="Cloudflare" />
  </p>
</div>

---

Un portfolio personale web dinamico, bilingue e responsivo costruito con **FastAPI** (Python) e **Vanilla JavaScript/CSS**. Progettato per essere veloce, leggero e facilmente manutenibile, con un'architettura divisa tra ambiente di sviluppo e produzione tramite **Docker** e deployment automatizzato.

<p align="center">
  <a href="https://www.stefanovidesott.com" target="_blank">
      <img src="https://img.shields.io/badge/🌐_Live_Demo-www.stefanovidesott.com-005571?style=for-the-badge" alt="Portfolio" />
  </a>
</p>

## ✨ Funzionalità Principali

* 🌍 **Multilingua (IT / EN):** Sistema di traduzione personalizzato tramite dizionari Python (`translations.py`) gestito da Jinja2. Include lo *Smart Routing* basato sull'header `Accept-Language` del browser dell'utente.
* 🌗 **Dark/Light Mode:** Tema scuro di default con switch manuale al tema chiaro salvato nel `localStorage`.
* 📧 **Form di Contatto Funzionante:** Endpoint API backend che utilizza `BackgroundTasks` di FastAPI e `smtplib` per inviare e-mail reali in background, senza bloccare la UI.
* 🛡️ **Sicurezza Avanzata:** Headers HTTP restrittivi (**CSP** e **HSTS**) implementati via Middleware per proteggere da attacchi XSS/Clickjacking. Integrazione nativa con **Cloudflare Turnstile**.
* ✅ **Test Automatizzati:** Test suite completa scritta con `pytest` per validare rotte, smart routing, gestione 404 e validazione dei payload API.
* 🚀 **CI/CD Pipeline Avanzata:** Deployment tramite **GitHub Actions**. Al push su `main`, la pipeline esegue i test. Se superati, si collega via SSH, minifica CSS e JS, aggiorna i container Docker e svuota automaticamente la cache di Cloudflare tramite API.
* 📊 **Analitiche Privacy-Friendly:** Tracciamento delle visite cookieless e GDPR-compliant tramite **Cloudflare Web Analytics** (caricato condizionalmente solo in produzione).
* ✨ **Animazioni UI Custom:** Effetti di comparsa allo scroll e *typing effect* scritti in puro Vanilla JS.

## 🛠️ Stack Tecnologico

* **Backend:** Python 3.10, FastAPI, Uvicorn, Jinja2, Pytest
* **Frontend:** HTML5, CSS3 (Custom Properties/Variables), Vanilla JavaScript
* **DevOps & Infrastructure:** Docker, Docker Compose, Nginx, GitHub Actions
* **Security & Analytics:** Cloudflare Turnstile, Cloudflare Web Analytics, Security Headers

## 📂 Struttura del Progetto

```text
portfolio-site/
├── .github/workflows/       # Pipeline CI/CD (deploy.yml)
├── app/
│   ├── main.py              # Logica API FastAPI, Middleware e routing
│   ├── translations.py      # Dizionari per il multilingua (IT/EN)
│   ├── static/              # Asset statici (CSS, JS, immagini, PDF)
│   ├── templates/           # Template HTML (Jinja2)
│   └── tests/               # Suite di test automatizzati (pytest)
├── .env.example             # Template per le variabili d'ambiente
├── docker-compose.yml       # Configurazione Docker (Produzione)
├── docker-compose.override.yml.dev # Configurazione Docker (Sviluppo locale)
├── Dockerfile               # Istruzioni build dell'immagine Python
├── README.md
└── requirements.txt         # Dipendenze Python
```

## 🚀 Come avviare il progetto in locale (Development)

1. **Clona la repository:**

```bash
git clone https://github.com/StefanoVidesott/portfolio-site.git
cd portfolio-site
```

2. **Configura le variabili d'ambiente:**
Crea un file `.env` (o rinomina `.env.example`) nella root del progetto e inserisci le tue credenziali:

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

CLOUDFLARE_WEB_ANALYTICS_TOKEN= # (lasciare vuoto in locale)
```

3. **Configura Docker Compose per lo sviluppo:**
Rinomina il file `docker-compose.override.yml.dev` in `docker-compose.override.yml`. (Questo file monta la cartella `app` per il live-reload e *non* va committato in produzione).
4. **Avvia il container Docker:**

```bash
docker compose up --build
```

*Il sito sarà disponibile all'indirizzo `http://localhost:8001` (o la porta configurata).*

5. **Esegui i Test Automatizzati:**
Per eseguire la test suite localmente:

```bash
docker exec -it <nome_container> python -m pytest
```

## 🚢 Messa in Produzione (Deployment)

Questo progetto sfrutta un approccio **CI/CD automatizzato**.
Ogni `git push` sul ramo `main` innesca una GitHub Action che esegue la suite di test. Solo se i test hanno successo, la pipeline si collega via SSH al server di produzione, minifica gli asset frontend, ricostruisce l'immagine Docker e svuota la cache di Cloudflare.

**Per il setup iniziale sul server:**

1. Clona la repository sul server e imposta `ENVIRONMENT=prod` nel file `.env`.
2. Inserisci i token reali di Cloudflare e le credenziali SMTP.
3. La porta esposta da Docker (es. `8001`) è progettata per essere servita tramite un reverse proxy **Nginx** con certificati SSL.
