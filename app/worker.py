import os
import time
import socket
from datetime import datetime

import httpx
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Target, Check

INTERVAL_SECONDS = int(os.getenv("WORKER_INTERVAL_SECONDS", "30"))
HTTP_TIMEOUT_SECONDS = float(os.getenv("WORKER_HTTP_TIMEOUT_SECONDS", "5"))
TCP_TIMEOUT_SECONDS = float(os.getenv("WORKER_TCP_TIMEOUT_SECONDS", "3"))


def check_http(url: str):
    start = time.perf_counter()
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT_SECONDS, follow_redirects=True) as client:
            r = client.get(url)
        latency_ms = (time.perf_counter() - start) * 1000.0
        ok = 200 <= r.status_code < 400
        return ok, r.status_code, latency_ms, None
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000.0
        return False, None, latency_ms, str(e)


def check_tcp(host: str, port: int):
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=TCP_TIMEOUT_SECONDS):
            pass
        latency_ms = (time.perf_counter() - start) * 1000.0
        return True, None, latency_ms, None
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000.0
        return False, None, latency_ms, str(e)


def run_once():
    db = SessionLocal()
    try:
        targets = db.execute(
            select(Target).where(Target.enabled == True)  # noqa: E712
        ).scalars().all()

        for t in targets:
            if t.type == "http":
                ok, status_code, latency_ms, error = check_http(t.target)
            elif t.type == "tcp":
                if not t.port:
                    continue
                ok, status_code, latency_ms, error = check_tcp(t.target, t.port)
            else:
                # icmp planned later
                continue

            c = Check(
                target_id=t.id,
                ok=ok,
                status_code=status_code,
                latency_ms=latency_ms,
                error=error,
                checked_at=datetime.utcnow(),
            )
            print(
                f"[worker] target_id={t.id} name={t.name} type={t.type} ok={ok} "
                f"status={status_code} latency_ms={latency_ms:.1f} error={error}"
            )
            db.add(c)

        db.commit()
    finally:
        db.close()


def main():
    print(f"[worker] starting, interval={INTERVAL_SECONDS}s")
    while True:
        run_once()
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()