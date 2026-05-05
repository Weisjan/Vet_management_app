from fastapi import APIRouter

from app.api.routes import ai_analysis, alerts, clinics, health, keywords, mentions
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])

versioned_router = APIRouter(prefix=settings.api_v1_prefix)
versioned_router.include_router(health.router, tags=["health"])
versioned_router.include_router(clinics.router)
versioned_router.include_router(keywords.router)
versioned_router.include_router(mentions.router)
versioned_router.include_router(ai_analysis.router)
versioned_router.include_router(alerts.router)

api_router.include_router(versioned_router)
