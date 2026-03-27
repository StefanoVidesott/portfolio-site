<div align="center">
  <h1>Stefano Videsott — Personal Portfolio</h1>

  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
    <img src="https://img.shields.io/badge/Alembic-5C6BC0?style=for-the-badge&logo=alembic&logoColor=white" alt="Alembic">
    <img src="https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3" alt="Pytest">
    <img src="https://img.shields.io/badge/Jinja-B41717?style=for-the-badge&logo=jinja&logoColor=white" alt="Jinja2">
    <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
    <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
    <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" alt="GitHub Actions">
    <img src="https://img.shields.io/badge/Cloudflare-F38020?style=for-the-badge&logo=cloudflare&logoColor=white" alt="Cloudflare">
  </p>

  <img src="https://img.shields.io/badge/🌐_Live-www.stefanovidesott.com-005571?style=for-the-badge" alt="Portfolio" />
</div>

---

My personal portfolio and the CMS that runs it. Built from scratch with FastAPI and vanilla JS — no framework, no third-party CMS, just the parts I actually needed. The admin panel generates forms dynamically by reading SQLAlchemy model metadata, so adding or modifying a content type doesn't require touching any template code.

The site is bilingual (IT/EN), uses SQLite on a Docker volume, and ships with a CI/CD pipeline that runs tests, minifies assets, migrates the database, and flushes the Cloudflare cache on every push to `main`.

## Running locally

Copy `.env.example` to `.env` and fill in your values, then:

```bash
docker compose -f docker-compose.yaml -f docker-compose.override.yml.dev up --build
```

On first run, create the database tables and seed the initial content:

```bash
docker exec -it portfolio_container alembic upgrade head
docker exec -it portfolio_container python seed.py
```

The site will be at `http://localhost:8001`. The admin panel is at `/en/admin`.

## Tests

```bash
docker exec -it portfolio_container python -m pytest
```

Or without a running container:

```bash
docker compose run --rm --no-deps -e ENVIRONMENT=dev portfolio python -m pytest -v
```

## Deployment

Push to `main`. The GitHub Actions workflow handles the rest: runs the test suite, SSHs into the server, rebuilds the Docker image, runs `alembic upgrade head`, and clears the Cloudflare cache. For the initial server setup, clone the repo, set `ENVIRONMENT=prod` in `.env`, and put Nginx in front of port `8001`.
