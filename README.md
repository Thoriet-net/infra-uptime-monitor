# Infra Uptime Monitor

A small SRE-flavoured uptime monitor for **URLs and IP-based targets**.  
Built to be **boring, predictable and reproducible**.

> Current state: API + DB + migrations  
> Next milestone: background worker performing checks

---

## What it does

- Stores monitoring targets in PostgreSQL
- Supports target types:
  - `http` (URL availability)
  - `tcp` (port availability)
  - `icmp` (ping – planned)
- Exposes a simple REST API
- Uses **Alembic migrations** for database schema management
- Runs fully locally via **Docker Compose**

---

## Architecture

```mermaid
flowchart LR
  Client[User / curl / browser] --> API[FastAPI API]
  API --> DB[(PostgreSQL)]

  subgraph Docker Compose
    API
    DB
  end
```

---

## Quickstart (local)

### Requirements
- Docker Desktop

### Run

```bash
docker compose up --build
```

API endpoints:
- Health check: http://localhost:8000/healthz
- Swagger UI: http://localhost:8000/docs

Stop:

```bash
Ctrl + C
```

Run in background:

```bash
docker compose up -d
docker compose logs -f
docker compose down
```

---

## Configuration

Create a `.env` file (not committed, see `.env.example`):

```env
APP_ENV=dev
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/uptime
```

---

## API usage

### Create monitoring target

```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Google",
    "type": "http",
    "target": "https://google.com",
    "enabled": true
  }'
```

### List targets

```bash
curl http://localhost:8000/targets
```

---

## Database migrations

Database schema is managed via **Alembic**.

Migrations are executed automatically when the API container starts:

```bash
alembic upgrade head && uvicorn ...
```

Manual commands (inside running container):

```bash
docker compose exec api alembic current
docker compose exec api alembic history
docker compose exec api alembic upgrade head
```

---

## Why this project

I’m transitioning from a networking-heavy background towards  
**SRE / platform engineering**.

This project focuses on:
- availability & monitoring mindset
- reproducible environments
- explicit database schema management
- clean separation between API and future worker logic

---

## Roadmap

- Background worker performing checks
- Store check results (status, latency, timestamp)
- Uptime history & simple status view
- Alerting (webhook / email)
- Kubernetes deployment (k3s-friendly)
- Optional Terraform cloud deployment

---

## License

MIT