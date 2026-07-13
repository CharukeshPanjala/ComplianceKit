from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from common.middleware.security_headers import SecurityHeadersMiddleware
from app.limiter import limiter
from app.routers.regulations import router as regulations_router
from app.routers.assessments import router as assessments_router
from app.routers.ropa import router as ropa_router
from app.routers.policies import router as policies_router
from app.routers.reports import router as reports_router
from app.routers.processors import router as processors_router
from app.routers.breach import router as breach_router
from app.routers.dsar import router as dsar_router
from app.routers.dpo_assistant import router as dpo_assistant_router
from app.config import settings

app = FastAPI(title="Policy Engine", version="0.1.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(regulations_router)
app.include_router(assessments_router)
app.include_router(ropa_router)
app.include_router(policies_router)
app.include_router(reports_router)
app.include_router(processors_router)
app.include_router(breach_router)
app.include_router(dsar_router)
app.include_router(dpo_assistant_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "policy-engine"}