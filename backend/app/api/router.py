from fastapi import APIRouter

from app.api.routes import health
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])

versioned_router = APIRouter(prefix=settings.api_v1_prefix)
versioned_router.include_router(health.router, tags=["health"])

api_router.include_router(versioned_router)
