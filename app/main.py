from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db, engine, Base
from app.models import Target
from app import models  # noqa: F401 (ensures models are imported)

app = FastAPI(title="Infra Uptime Monitor", version="0.1.0")

@app.on_event("startup")
def on_startup():
    # Temporary approach: create tables automatically.
    # We'll replace this with Alembic migrations in the next milestone.
    Base.metadata.create_all(bind=engine)

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