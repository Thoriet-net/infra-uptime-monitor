# Roadmap

This document outlines the planned evolution of the Infra Uptime Monitor project.

The roadmap is intentionally pragmatic.  
Features are added only when they demonstrate a real operational or architectural concept.

---

## Phase 1 – Core Monitoring (Completed)

Goal: build a minimal but production-shaped monitoring system.

Completed features:

- HTTP monitoring
- TCP monitoring
- ICMP (ping) monitoring
- Asynchronous worker architecture
- Check persistence in PostgreSQL
- Uptime aggregation endpoint
- Simple Web UI (HTML + JSON)
- Docker Compose deployment
- Kubernetes deployment
- Alembic-based database migrations

This phase validates:
- separation of concerns
- deployability across environments
- operational stability

---

## Phase 2 – Operational Readiness (Planned)

Goal: make the system safer and more production-aware.

Planned features:

- Alerting
  - webhook-based notifications
  - simple threshold rules
- Retention policies
  - automatic cleanup of old check records
- Structured logging
- Improved error visibility
- Configuration validation at startup

This phase focuses on day-2 operations.

---

## Phase 3 – Observability & Scaling (Planned)

Goal: visibility and scalability.

Planned features:

- Prometheus metrics endpoint
- Grafana dashboards
- Multiple worker replicas
- Horizontal scaling experiments
- Load testing of API endpoints

This phase demonstrates how the architecture behaves under load.

---

## Phase 4 – Infrastructure as Code (Planned)

Goal: fully reproducible infrastructure.

Planned features:

- Terraform-based infrastructure provisioning
- Remote Terraform state (S3 backend + locking)
- Kubernetes cluster provisioning
- Network and firewall rules
- Secrets management strategy

Terraform is intentionally separated from application deployment logic.

---

## Phase 5 – Security & Hardening (Optional)

Goal: demonstrate security awareness.

Possible features:

- Authentication and authorization
- Role-based access control
- API rate limiting
- Network policies in Kubernetes
- Secrets rotation

These topics are intentionally postponed until the core system is stable.

---

## Non-Goals

The following are explicitly out of scope:

- SaaS-level feature completeness
- UI-heavy frontend development
- Multi-tenant support

The project prioritizes **clarity over complexity**.

---

## Notes

This roadmap is flexible.

The project is designed as a learning and demonstration tool rather than a commercial product.
Each phase can be discussed independently during technical interviews.
