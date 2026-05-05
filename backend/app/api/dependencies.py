from typing import Annotated

from fastapi import Depends
from rq import Queue
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.workers.connection import get_queue

DbSession = Annotated[Session, Depends(get_db)]


def get_background_queue() -> Queue:
    return get_queue("ai")


BackgroundQueue = Annotated[Queue, Depends(get_background_queue)]


def get_current_user_id() -> None:
    # Authentication is intentionally not implemented yet.
    # Keep this dependency as the future auth insertion point for routers/services.
    return None
