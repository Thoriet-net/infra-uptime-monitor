import os
import time
import socket
import re
import subprocess
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select, delete

from app.db import SessionLocal
from app.models import Target, Check

INTERVAL_SECONDS = int(os.getenv("WORKER_INTERVAL_SECONDS", "30"))
HTTP_TIMEOUT_SECONDS = float(os.getenv("WORKER_HTTP_TIMEOUT_SECONDS", "5"))
TCP_TIMEOUT_SECONDS = float(os.getenv("WORKER_TCP_TIMEOUT_SECONDS", "3"))
ICMP_TIMEOUT_SECONDS = float(os.getenv("WORKER_ICMP_TIMEOUT_SECONDS", "3"))
RETENTION_DAYS = int(os.getenv("CHECK_RETENTION_DAYS", "7"))

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

def check_icmp(host: str, ip_version: int = 4):
    """ICMP check using the system `ping` binary (Linux inside container).

    Notes:
    - In Docker Compose and Kubernetes, this runs inside a Linux container, so we rely on `iputils-ping`.
    - We try to parse RTT from stdout ("time=... ms"). If parsing fails, we fall back to wall-clock runtime.
    """
    start = time.perf_counter()
    try:
        # `-W` is in seconds for iputils ping (Linux). Keep it integer.
        timeout_s = max(1, int(ICMP_TIMEOUT_SECONDS))

        # Keep a hard subprocess timeout slightly above ping timeout, so the worker never hangs.
        hard_timeout = float(timeout_s) + 1.0

        cmd = ["ping", "-c", "1", "-W", str(timeout_s), host]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=hard_timeout,
        )

        wall_ms = (time.perf_counter() - start) * 1000.0
        ok = result.returncode == 0

        # Prefer RTT from output when available.
        rtt_ms = None
        m = re.search(r"time=([0-9.]+)\s*ms", result.stdout)
        if m:
            try:
                rtt_ms = float(m.group(1))
            except ValueError:
                rtt_ms = None

        latency_ms = rtt_ms if rtt_ms is not None else wall_ms

        if ok:
            return True, None, latency_ms, None

        # Keep error short but informative
        err = (result.stderr or "").strip() or f"ping failed (rc={result.returncode})"
        return False, None, latency_ms, err

    except subprocess.TimeoutExpired:
        wall_ms = (time.perf_counter() - start) * 1000.0
        return False, None, wall_ms, "ping timed out"
    except Exception as e:
        wall_ms = (time.perf_counter() - start) * 1000.0
        return False, None, wall_ms, str(e)  

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
            elif t.type == "icmp":
                ok, status_code, latency_ms, error = check_icmp(t.target)
            else:
                continue

            c = Check(
                target_id=t.id,
                ok=ok,
                status_code=status_code,
                latency_ms=latency_ms,
                error=error,
                checked_at=datetime.now(timezone.utc),
            )
            print(
                f"[worker] target_id={t.id} name={t.name} type={t.type} ok={ok} "
                f"status={status_code} latency_ms={latency_ms:.1f} error={error}"
            )
            db.add(c)

        cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
        db.execute(delete(Check).where(Check.checked_at < cutoff))

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