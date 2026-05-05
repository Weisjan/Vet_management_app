from fastapi import APIRouter

from app.db.health import check_database
from app.workers.health import check_redis

router = APIRouter()


@router.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def ready() -> dict[str, str | dict[str, str]]:
    database = check_database()
    redis = check_redis()
    status = "ok" if database["status"] == "ok" and redis["status"] == "ok" else "degraded"

    return {
        "status": status,
        "checks": {
            "database": database["status"],
            "redis": redis["status"],
        },
    }


@router.get("/health")
def health() -> dict[str, str | dict[str, str]]:
    readiness = ready()
    return {
        "status": readiness["status"],
        "service": "api",
        "checks": readiness["checks"],
    }
