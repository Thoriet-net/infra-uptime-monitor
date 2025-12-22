# Infra Uptime Monitor

Simple uptime monitoring service for HTTP, TCP and ICMP targets.

This project was built primarily to explore and compare different deployment strategies:
- local development using Docker Compose
- container orchestration using Kubernetes

The application logic is intentionally simple. The main focus is infrastructure, deployment flow and operational behavior.

---

## Features

- Monitor HTTP, TCP and ICMP targets
- Background worker for executing checks
- REST API built with FastAPI
- Simple Web UI for managing targets
- Uptime statistics and history
- PostgreSQL database
- Database migrations via Alembic

---

## Architecture Overview

The application is split into multiple components:

### API
- Handles HTTP requests
- Manages targets and exposes monitoring data
- Stateless and lightweight
- Designed to respond quickly

### Worker
- Runs independently from the API
- Periodically executes uptime checks
- Supports HTTP, TCP and ICMP probes
- Can be scaled separately from the API

### Database
- PostgreSQL
- Stores targets and check history
- Shared by API and worker

---

## Quick Start (Docker Compose)

Run the full stack locally using Docker Compose.

### Start services (foreground)

```bash
docker compose up --build
```

### Start services in background

```bash
docker compose up -d --build
```

### Stop and remove services

```bash
docker compose down
```

### Available endpoints

- API: http://localhost:8000
- Web UI: http://localhost:8000/ui
- Swagger UI: http://localhost:8000/docs

---

## Kubernetes Deployment

The same application can be deployed to Kubernetes (tested with `kind`).

Kubernetes deployment demonstrates:
- separation of API and worker workloads
- self-healing via pod restarts
- database migrations via a Kubernetes Job

Detailed instructions are available in `docs/kubernetes.md`.

---

## Documentation

Additional documentation is split into smaller focused files:

- `docs/architecture.md`
- `docs/api.md`
- `docs/docker-compose.md`
- `docs/kubernetes.md`
- `docs/terraform.md` (planned)
- `docs/roadmap.md`

---

## Project Motivation

The goal of this project was not feature complexity, but hands-on experience with:

- real-world deployment patterns
- separation of API and background processing
- Docker Compose vs Kubernetes behavior
- preparing a clean base for future cloud deployment

---

## License

MIT
```