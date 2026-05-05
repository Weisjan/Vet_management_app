import logging

from app.workers.connection import get_redis_connection

logger = logging.getLogger(__name__)


def check_redis() -> dict[str, str]:
    try:
        redis = get_redis_connection()
        redis.ping()
        return {"status": "ok"}
    except Exception:
        logger.exception("Redis health check failed")
        return {"status": "error"}
