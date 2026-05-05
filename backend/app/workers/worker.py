import logging

from rq import Worker

from app.core.config import settings
from app.core.logging import configure_logging
from app.workers.connection import get_redis_connection


def main() -> None:
    configure_logging()
    redis = get_redis_connection()
    logger = logging.getLogger(__name__)
    logger.info("Starting RQ worker", extra={"queues": settings.queue_names})
    worker = Worker(settings.queue_names, connection=redis)
    worker.work()


if __name__ == "__main__":
    main()
