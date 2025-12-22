# Docker Compose Deployment

This document describes how Infra Uptime Monitor is run locally using Docker Compose.

Docker Compose is used as the simplest way to run the full application stack on a single machine
for development, testing, and experimentation.

---

## Goals of the Docker Compose setup

The main goals of the Docker Compose deployment are:

- easy local startup
- minimal configuration
- fast iteration during development
- single-host execution
- clear separation between API and background worker

The application code is identical to the Kubernetes setup.
Only the deployment layer changes.

---

## Services

### API Service

- Runs the FastAPI application
- Exposes REST API and Web UI
- Listens on port 8000
- Stateless
- Handles all incoming HTTP requests

The API must stay responsive and should not perform long-running monitoring tasks.

---

### Worker Service

- Runs background monitoring logic
- Periodically checks all enabled targets
- Supports HTTP, TCP and ICMP probes
- Has longer timeouts and heavier workload than the API
- Runs independently of API request handling

Separating the worker prevents slow checks from blocking API responses.

---

### PostgreSQL Service

- Local PostgreSQL database
- Stores targets and check history
- Data is persisted using a Docker volume

This database is intended only for local development.
In production, a managed database service would be used instead.

---

## Startup Flow

Typical startup order when running Docker Compose:

1. PostgreSQL container starts
2. API container starts
3. Worker container starts and begins monitoring

Migrations are executed automatically during startup.

---

## Running the stack

Start the full stack in the foreground:

```
docker compose up --build
```

Start the stack in the background:

```
docker compose up -d --build
```

Stop and remove containers:

```
docker compose down
```

---

## Accessing the application

Once running:

- API: http://localhost:8000
- Web UI: http://localhost:8000/ui
- Swagger UI: http://localhost:8000/docs

---

## Differences from Kubernetes

Docker Compose:
- single host
- simple networking
- no self-healing
- no jobs for one-time tasks
- ideal for development and learning

Kubernetes:
- multi-process orchestration
- self-healing workloads
- explicit migration jobs
- closer to production environments

---

## Why Docker Compose here?

Docker Compose is used to:

- quickly validate application behavior
- test monitoring logic locally
- debug API and worker interaction
- provide a low-friction entry point into the project

It is intentionally simple and optimized for local use.
