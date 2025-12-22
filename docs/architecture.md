# Architecture

This project is a small but production-oriented uptime monitoring system.
Its primary goal is not feature richness, but to demonstrate **clean separation
of concerns**, **deployability in multiple environments**, and **operational thinking**.

---

## High-level Overview

The system consists of four main components:

- **API service**
- **Worker service**
- **PostgreSQL database**
- **Deployment layer** (Docker Compose or Kubernetes)

Each component has a clearly defined responsibility and failure boundary.

---

## Diagram

### System view (logical)

```mermaid
flowchart LR
    User[User / Operator]
    API[API (FastAPI)<br/>REST + Web UI]
    Worker[Worker<br/>Background checks]
    DB[(PostgreSQL)]

    User -->|HTTP| API
    API -->|Read/Write| DB
    Worker -->|Read targets| DB
    Worker -->|Write checks| DB
```

### System view (ASCII fallback)

```
+------------------+        HTTP        +---------------------------+
|  User / Browser  |  <------------->  |  API (FastAPI)            |
+------------------+                   |  REST + Web UI            |
                                       +-------------+-------------+
                                                     |
                                                     | SQL (read/write)
                                                     v
                                             +---------------+
                                             |  PostgreSQL   |
                                             +-------+-------+
                                                     ^
                                                     |
                                     SQL (write checks/results)
                                                     |
                                             +---------------+
                                             |    Worker     |
                                             |  HTTP/TCP/ICMP |
                                             +---------------+
```

---

## Components

### API Service

The API is a lightweight FastAPI application responsible for:

- accepting HTTP requests
- managing monitored targets
- exposing monitoring results (checks, uptime)
- serving a simple web UI

Key properties:

- **stateless**
- **fast startup**
- **no blocking or long-running operations**
- horizontally scalable

The API never performs monitoring itself.  
All monitoring work is delegated to the worker.

---

### Worker Service

The worker is a background process responsible for:

- periodically loading enabled targets from the database
- performing health checks:
  - HTTP
  - TCP
  - ICMP (ping)
- storing results as check records

Key properties:

- runs continuously
- tolerates slow or failing targets
- can be restarted independently of the API
- designed for future horizontal scaling

This separation ensures that slow network operations never impact API latency.

---

### Database (PostgreSQL)

PostgreSQL is used as a shared state store for:

- monitored targets
- individual check results
- uptime calculations

Schema migrations are managed via **Alembic** and executed explicitly
(e.g. via a migration job in Kubernetes).

The database is treated as an external dependency and not coupled to application startup.

---

## Deployment Models

The same application code runs in two different deployment models.

### Docker Compose (Local Development)

Used for:

- local development
- quick testing
- simple demonstrations

Characteristics:

- single-node setup
- manual restarts
- ports exposed directly on localhost
- minimal operational overhead

---

### Kubernetes (Production-oriented Setup)

Used to demonstrate:

- container orchestration concepts
- self-healing workloads
- separation of runtime concerns

Characteristics:

- API and worker run as separate Deployments
- PostgreSQL runs as its own Deployment
- database migrations executed via a Job
- automatic restarts on failure
- API access via `kubectl port-forward` in local clusters

Kubernetes does **not** change application behavior —
only how components are supervised and restarted.

---

## Data Flow

1. User creates or manages targets via the API (REST or Web UI)
2. Targets are stored in PostgreSQL
3. Worker periodically loads enabled targets
4. Worker performs checks and stores results
5. API reads stored results and exposes them to users

All communication between API and worker happens **indirectly via the database**.

---

## Design Principles

- separation of concerns
- explicit ownership of responsibilities
- failure isolation
- environment-agnostic application code
- operational transparency

This project intentionally avoids overengineering while still reflecting
real-world production patterns.

---

## Future Extensions

Planned or possible future improvements:

- alerting (email / webhook)
- metrics export (Prometheus)
- authentication & authorization
- multi-worker scaling
- infrastructure provisioning via Terraform

These are intentionally out of scope for the initial implementation.
