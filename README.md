<div align="center">
  <h1>Stefano Videsott - Personal Portfolio 🚀</h1>

  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Jinja-B41717?style=for-the-badge&logo=jinja&logoColor=white" alt="Jinja2" />
    <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
    <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
    <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3" />
    <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  </p>
</div>

---

Un portfolio personale web dinamico, bilingue e responsivo costruito con **FastAPI** (Python) e **Vanilla JavaScript/CSS**. Progettato per essere veloce, leggero e facilmente manutenibile, con un'architettura divisa tra ambiente di sviluppo e produzione tramite **Docker**.

🌐 **Live Demo:** [www.stefanovidesott.com](https://www.stefanovidesott.com)

## ✨ Funzionalità Principali

* 🌍 **Multilingua (IT / EN):** Sistema di traduzione personalizzato tramite dizionari Python (`translations.py`) gestito da Jinja2. Include lo *Smart Routing* basato sull'header `Accept-Language` del browser dell'utente.
* 🌗 **Dark/Light Mode:** Tema scuro di default con switch manuale al tema chiaro.
* 📧 **Form di Contatto Funzionante:** Endpoint API backend che utilizza `BackgroundTasks` di FastAPI e `smtplib` per inviare e-mail reali in background, senza bloccare la UI.
* ✨ **Animazioni UI Custom:** Effetto macchina da scrivere (Typing Effect) ed effetti di comparsa allo scroll (Scroll Reveal) scritti in puro Vanilla JS.
* 🐳 **Pronto per la Produzione:** Setup Docker multi-ambiente. Caricamento dinamico di asset minificati (`-min.css`, `-min.js`) in ambiente di produzione.
* 🔍 **SEO & UX:** `sitemap.xml`, `robots.txt`, meta tag completi e pagina 404 personalizzata.

## 🛠️ Stack Tecnologico

* **Backend:** Python 3.10, FastAPI, Uvicorn, Jinja2
* **Frontend:** HTML5, CSS3 (Custom Properties/Variables), Vanilla JavaScript
* **DevOps & Deploy:** Docker, Docker Compose

## 📂 Struttura del Progetto

```text
portfolio/
├── app/
│   ├── main.py              # Logica principale FastAPI e routing
│   ├── translations.py      # Dizionari per il multilingua (IT/EN)
│   ├── static/              # Asset statici
│   │   ├── css/             # File CSS (normali e minificati)
│   │   ├── js/              # File JS (normali e minificati)
│   │   ├── images/          # Immagini e icone
│   │   └── docs/            # CV e documenti PDF dei progetti
│   └── templates/           # Template HTML Jinja2
├── .env                     # Variabili d'ambiente
├── .gitignore
├── docker-compose.yml       # Configurazione Docker per la produzione
├── docker-compose.override.yml # Configurazione Docker per lo sviluppo locale (volumi/reload)
├── Dockerfile               # Istruzioni build dell'immagine Python
├── README.md
└── requirements.txt
```

## 🚀 Come avviare il progetto in locale (Development)

1. **Clona la repository:**
```bash
git clone https://github.com/StefanoVidesott/portfolio-site.git
cd portfolio-site
```


2. **Configura le variabili d'ambiente:**
Crea un file `.env` (o rinomina .env.example) nella root del progetto e inserisci le tue credenziali:
```env
ENVIRONMENT=dev

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SENDER_EMAIL=la_tua_email@gmail.com
SENDER_PASSWORD=la_tua_app_password
RECEIVER_EMAIL=la_tua_email@gmail.com
```

3. **Configura Docker Compose per lo sviluppo:**
Rinomina il file `docker-compose.override.yml.dev` in `docker-compose.override.yml` nella root (questo file monta la cartella `app` per il live-reload e *non* va committato in produzione).
4. **Avvia il container Docker:**
```bash
docker compose up --build
```


*Il sito sarà disponibile all'indirizzo `http://localhost:8001` (o la porta che hai configurato).*

## 🚢 Messa in Produzione (Deployment)

Per il deploy sul server, assicurati di:

1. Impostare `ENVIRONMENT=prod` nel file `.env` sul server (questo forzerà Jinja a caricare le versioni minificate di CSS e JS).
2. Rinominare o rimuovere il file `docker-compose.override.yml`.
3. Avviare Docker Compose in modalità detached:
```bash
docker compose up -d --build
```

## 👨‍💻 Autore

**Stefano Videsott**

* LinkedIn: [linkedin.com/in/stefano-videsott](https://linkedin.com/in/stefano-videsott)
* GitHub: [@StefanoVidesott](https://github.com/StefanoVidesott)
