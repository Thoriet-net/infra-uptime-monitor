from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, func, delete
from pathlib import Path

from app.db import get_db
from app.models import Target, Check

app = FastAPI(title="Infra Uptime Monitor", version="0.1.0")

app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")

@app.get("/")
def root():
    return RedirectResponse(url="/ui")


def get_target_or_404(db: Session, target_id: int) -> Target:
    t = db.get(Target, target_id)
    if t is None:
        raise HTTPException(status_code=404, detail="Target not found")
    return t


@app.get("/healthz")
def healthz():
    return {"ok": True}


class TargetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    type: str = Field(pattern="^(http|tcp|icmp)$")
    target: str = Field(min_length=1, max_length=512)
    port: int | None = Field(default=None, ge=1, le=65535)
    enabled: bool = True


@app.post("/targets")
def create_target(payload: TargetCreate, db: Session = Depends(get_db)):
    if payload.type == "tcp" and payload.port is None:
        raise HTTPException(status_code=400, detail="TCP target requires port.")
    if payload.type != "tcp" and payload.port is not None:
        raise HTTPException(status_code=400, detail="Port is only allowed for TCP targets.")

    t = Target(**payload.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"id": t.id, **payload.model_dump()}


@app.get("/targets")
def list_targets(db: Session = Depends(get_db)):
    rows = db.execute(select(Target).order_by(Target.id)).scalars().all()
    return [
        {"id": t.id, "name": t.name, "type": t.type, "target": t.target, "port": t.port, "enabled": t.enabled}
        for t in rows
    ]


@app.get("/targets/{target_id}/checks")
def list_checks(
    target_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=200),
):
    get_target_or_404(db, target_id)

    rows = db.execute(
        select(Check)
        .where(Check.target_id == target_id)
        .order_by(Check.checked_at.desc())
        .limit(limit)
    ).scalars().all()

    return [
        {
            "id": c.id,
            "target_id": c.target_id,
            "ok": c.ok,
            "status_code": c.status_code,
            "latency_ms": c.latency_ms,
            "error": c.error,
            "checked_at": c.checked_at.isoformat(),
        }
        for c in rows
    ]


@app.get("/targets/{target_id}/uptime")
def uptime(
    target_id: int,
    hours: int = Query(default=24, ge=1, le=720),
    db: Session = Depends(get_db),
):
    get_target_or_404(db, target_id)

    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    total = db.execute(
        select(func.count())
        .select_from(Check)
        .where(Check.target_id == target_id)
        .where(Check.checked_at >= since)
    ).scalar_one()

    ok = db.execute(
        select(func.count())
        .select_from(Check)
        .where(Check.target_id == target_id)
        .where(Check.checked_at >= since)
        .where(Check.ok == True)  # noqa
    ).scalar_one()

    uptime = 100.0 if total == 0 else round((ok / total) * 100.0, 2)

    return {
        "target_id": target_id,
        "window_hours": hours,
        "total_checks": total,
        "ok_checks": ok,
        "uptime_percent": uptime,
    }

@app.delete("/targets/{target_id}")
def delete_target(target_id: int, db: Session = Depends(get_db)):
    # check existence
    t = db.get(Target, target_id)
    if not t:
        raise HTTPException(status_code=404, detail="Target not found")

    # delete checks first (avoid FK issues)
    db.execute(delete(Check).where(Check.target_id == target_id))
    db.execute(delete(Target).where(Target.id == target_id))
    db.commit()

    return {"ok": True, "deleted_target_id": target_id}