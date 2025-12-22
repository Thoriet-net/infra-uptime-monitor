# Kubernetes Deployment

This document describes how to run **Infra Uptime Monitor** on Kubernetes (local development using `kind`).

The Kubernetes setup mirrors the Docker Compose setup but uses Kubernetes primitives
(Deployments, Services, Jobs) and requires explicit port forwarding for local access.

---

## Components

The Kubernetes deployment consists of:

- **api** – FastAPI application (HTTP API + Web UI)
- **worker** – background worker performing checks (HTTP / TCP / ICMP)
- **postgres** – PostgreSQL database
- **migrate job** – one-shot Alembic migration job

---

## Prerequisites

- Docker Desktop (with Kubernetes enabled) **or** `kind`
- `kubectl`
- Built Docker image:
  ```bash
  docker build -t infra-uptime-monitor:local .
  kind load docker-image infra-uptime-monitor:local --name uptime
  ```

---

## Namespace

All resources are deployed into the `uptime` namespace.

```bash
kubectl create namespace uptime
```

---

## Deploy order

Apply manifests in this order:

```bash
kubectl apply -f k8s/01-postgres.yaml
kubectl apply -f k8s/02b-migrate-job.yaml
kubectl apply -f k8s/03-api.yaml
kubectl apply -f k8s/04-worker.yaml
```

Wait until everything is running:

```bash
kubectl -n uptime get pods
```

---

## Database migrations

Migrations are handled by a **Kubernetes Job** (`migrate`).

You can verify migration logs with:

```bash
kubectl -n uptime logs job/migrate
```

---

## Accessing the API and Web UI (IMPORTANT)

Unlike Docker Compose, Kubernetes **does not expose services to localhost automatically**.

You must use **port-forwarding**.

### Port-forward API service

```bash
kubectl -n uptime port-forward svc/api 18000:8000
```

After that:

- API: http://localhost:18000
- Health check: http://localhost:18000/healthz
- Web UI: http://localhost:18000/ui
- Swagger: http://localhost:18000/docs

⚠️ **Without port-forwarding, the API and UI are NOT reachable from your browser.**

This is expected behavior in Kubernetes.

---

## Worker behavior

- Worker runs continuously in the background
- Performs checks every configured interval
- Uses ICMP (`ping`) inside the container
- Automatically restarts if it crashes

Check worker logs:

```bash
kubectl -n uptime logs deploy/worker
```

---

## Restarting components

```bash
kubectl -n uptime rollout restart deploy/api
kubectl -n uptime rollout restart deploy/worker
```

---

## Key differences vs Docker Compose

| Docker Compose | Kubernetes |
|---------------|------------|
| Services exposed automatically | Port-forward required |
| Single-node local setup | Cluster-style deployment |
| Manual restarts | Automatic restarts |
| Simple networking | Explicit networking |

---

## Notes

- This setup is intended for **local development and learning**
- In real cloud environments, port-forwarding would be replaced by:
  - Ingress
  - LoadBalancer
  - API Gateway

---
