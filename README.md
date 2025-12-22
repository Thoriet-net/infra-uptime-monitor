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
# Infra Uptime Monitor

A small, production-oriented uptime monitoring service.

The goal of this project is **not feature richness**, but to demonstrate:

- clean service separation
- multiple deployment models
- operational thinking
- infrastructure readiness

The same application runs **locally via Docker Compose** and **production-style via Kubernetes**.

---

## What the application does

The system monitors availability of:

- HTTP endpoints
- TCP services
- ICMP (ping) targets

For each target it records:

- availability (ok / failed)
- response status (if applicable)
- latency
- uptime over a selected time window

---

## Architecture overview

The system consists of three core components:

- **API** – FastAPI service handling requests and Web UI
- **Worker** – background process performing network checks
- **PostgreSQL** – shared persistent storage

The API never performs monitoring itself. All checks are executed asynchronously by the worker.

Both services communicate **only via the database**, which keeps the API responsive and allows the worker to run with longer timeouts.

A detailed architecture description and diagram can be found in `docs/architecture.md`.

---

## Deployment models

### Docker Compose (local development)

Best suited for:

- local development
- experimentation
- quick demos

Characteristics:

- single-node setup
- ports exposed directly on localhost
- manual restarts

### Kubernetes (production-oriented setup)

Used to demonstrate:

- workload separation (API vs worker)
- self-healing services
- database migrations via Kubernetes Job
- independent scaling of components

Local clusters (e.g. `kind`) access the API via port-forwarding.

---

## Quick start

### Docker Compose

Start services in foreground:

```bash
docker compose up --build
```

Run services in background:

```bash
docker compose up -d --build
```

Stop and remove services:

```bash
docker compose down
```

API and UI will be available at:

```
http://localhost:8000
```

---

### Kubernetes (local cluster)

Apply manifests:

```bash
kubectl apply -f k8s/
```

Forward API port:

```bash
kubectl -n uptime port-forward svc/api 18000:8000
```

API and UI will be available at:

```
http://localhost:18000
```

Detailed Kubernetes notes are available in `docs/kubernetes.md`.

---

## Web UI

A minimal HTML-based Web UI is served by the API.

It allows:

- listing targets
- adding new targets
- removing unwanted targets
- viewing recent checks and uptime

The UI communicates directly with the JSON API and is intentionally kept simple.

---

## Documentation

Additional documentation is split into focused files:

- `docs/architecture.md`
- `docs/api.md`
- `docs/docker-compose.md`
- `docs/kubernetes.md`
- `docs/terraform.md` (planned)
- `docs/roadmap.md`

---

## Roadmap

Phase 1 is complete and focuses on:

- core monitoring functionality
- Docker Compose and Kubernetes deployments
- background worker model
- basic Web UI
- uptime calculation

Future phases will add alerting, observability and infrastructure provisioning.

See `docs/roadmap.md` for details.

---

## Project motivation

This project was built as a **learning and portfolio project** to:

- compare Docker Compose and Kubernetes in practice
- design clean service boundaries
- understand operational trade-offs
- prepare a base for future cloud deployment

---

## License

MIT