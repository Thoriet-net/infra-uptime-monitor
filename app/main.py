from fastapi import FastAPI

app = FastAPI(title="Infra Uptime Monitor", version="0.0.1")

@app.get("/healthz")
def healthz():
    return {"ok": True}
