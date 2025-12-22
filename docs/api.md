# API Documentation

This document describes the REST API exposed by the Infra Uptime Monitor service.

The API is intentionally simple and stateless. It is designed to be used by:
- CLI tools (curl, scripts)
- Web UI (HTML + JSON)
- Future integrations (alerts, dashboards, Terraform, etc.)

All responses are JSON.

---

## Base URL

Docker Compose (local):
http://localhost:8000

Kubernetes (via port-forward):
http://localhost:18000

---

## Health Check

### GET /healthz

Basic liveness endpoint.

Response:
{
  "ok": true
}

Used by:
- Kubernetes readiness / liveness probes
- Manual sanity checks

---

## Targets

A target represents something that is monitored:
- HTTP endpoint
- TCP service
- ICMP host (ping)

### Target object

{
  "id": number,
  "name": string,
  "type": "http" | "tcp" | "icmp",
  "target": string,
  "port": number | null,
  "enabled": boolean
}

---

### GET /targets

Returns all configured targets.

Response:
[
  {
    "id": 1,
    "name": "Google",
    "type": "http",
    "target": "https://google.com",
    "port": null,
    "enabled": true
  }
]

---

### POST /targets

Creates a new monitoring target.

Request body:
{
  "name": "Cloudflare DNS",
  "type": "tcp",
  "target": "1.1.1.1",
  "port": 53,
  "enabled": true
}

Validation rules:
- type must be one of: http, tcp, icmp
- tcp targets require a port
- http and icmp targets must not specify a port

Response:
{
  "id": 2,
  "name": "Cloudflare DNS",
  "type": "tcp",
  "target": "1.1.1.1",
  "port": 53,
  "enabled": true
}

---

## Checks

A check represents a single monitoring result produced by the worker.

Checks are written asynchronously by the worker process.

### Check object

{
  "id": number,
  "target_id": number,
  "ok": boolean,
  "status_code": number | null,
  "latency_ms": number | null,
  "error": string | null,
  "checked_at": string (ISO 8601)
}

---

### GET /targets/{id}/checks

Returns recent checks for a given target.

Query parameters:
- limit (optional, default: 20)

Example:
GET /targets/1/checks?limit=5

Response:
[
  {
    "id": 10,
    "target_id": 1,
    "ok": true,
    "status_code": 200,
    "latency_ms": 243.1,
    "error": null,
    "checked_at": "2025-12-19T08:31:51Z"
  }
]

---

## Uptime

The uptime endpoint aggregates historical checks.

### GET /targets/{id}/uptime

Query parameters:
- hours (optional, default: 24)

Example:
GET /targets/1/uptime?hours=1

Response:
{
  "target_id": 1,
  "window_hours": 1,
  "total_checks": 60,
  "ok_checks": 60,
  "uptime_percent": 100.0
}

If the target does not exist:
HTTP 404
{
  "detail": "Target not found"
}

---

## Error Handling

Errors follow standard FastAPI JSON responses.

Example:
HTTP 400
{
  "detail": "TCP target requires port."
}

---

## Notes

- The API is intentionally minimal.
- Authentication is not implemented (out of scope for this project).
- All writes are synchronous, all checks are asynchronous.
- The API process must stay responsive at all times; heavy work is delegated to the worker.

---

## Related Documentation

- docs/architecture.md
- docs/docker-compose.md
- docs/kubernetes.md
- docs/roadmap.md
