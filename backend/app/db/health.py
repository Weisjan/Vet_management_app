import logging

from sqlalchemy import text

from app.db.session import engine

logger = logging.getLogger(__name__)


def check_database() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        logger.exception("Database health check failed")
        return {"status": "error"}
