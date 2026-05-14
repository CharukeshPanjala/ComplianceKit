from fastapi import APIRouter
from .endpoints import health, webhooks, profile

router = APIRouter(prefix="/api/v1")

router.include_router(health.router, tags=["health"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
router.include_router(profile.router, prefix="/profile", tags=["profile"])
