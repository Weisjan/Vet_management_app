from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from rq import Queue
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.models.clinic import ClinicMember
from app.db.models.user import User
from app.db.session import get_db
from app.workers.connection import get_queue

DbSession = Annotated[Session, Depends(get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_background_queue() -> Queue:
    return get_queue("ai")


BackgroundQueue = Annotated[Queue, Depends(get_background_queue)]


def get_current_user(
    db: DbSession,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_access_token(token)
    except (jwt.InvalidTokenError, ValueError):
        raise credentials_error

    user = db.get(User, user_id)
    if user is None:
        raise credentials_error
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_clinic_membership(db: Session, user: User, clinic_id: UUID) -> ClinicMember:
    membership = db.scalars(
        select(ClinicMember).where(
            ClinicMember.clinic_id == clinic_id,
            ClinicMember.user_id == user.id,
        )
    ).first()
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found")
    return membership
