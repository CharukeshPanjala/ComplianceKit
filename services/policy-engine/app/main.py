from fastapi import FastAPI
from app.routers.regulations import router as regulations_router

app = FastAPI(title="Policy Engine", version="0.1.0")

app.include_router(regulations_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "policy-engine"}