from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import BackgroundQueue, CurrentUser, DbSession, require_clinic_membership
from app.modules.mentions.schemas import MentionCreate, MentionRead, MentionUpdate
from app.modules.mentions.service import (
    ClinicNotFoundForMentionError,
    MentionNotFoundError,
    MentionService,
)
from app.workers.jobs import process_new_mention

router = APIRouter(tags=["mentions"])


@router.get("/clinics/{clinic_id}/mentions", response_model=list[MentionRead])
def list_mentions(
    clinic_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[MentionRead]:
    require_clinic_membership(db, current_user, clinic_id)
    try:
        return MentionService(db).list_mentions(clinic_id=clinic_id, offset=offset, limit=limit)
    except ClinicNotFoundForMentionError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found") from exc


@router.post(
    "/clinics/{clinic_id}/mentions",
    response_model=MentionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_mention(
    clinic_id: UUID,
    payload: MentionCreate,
    db: DbSession,
    queue: BackgroundQueue,
    current_user: CurrentUser,
) -> MentionRead:
    require_clinic_membership(db, current_user, clinic_id)
    try:
        mention = MentionService(db).create_mention(clinic_id=clinic_id, data=payload)
    except ClinicNotFoundForMentionError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found") from exc

    queue.enqueue(process_new_mention, str(mention.id))
    return mention


@router.get("/mentions/{mention_id}", response_model=MentionRead)
def get_mention(
    mention_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> MentionRead:
    try:
        mention = MentionService(db).get_mention(mention_id)
        require_clinic_membership(db, current_user, mention.clinic_id)
        return mention
    except MentionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mention not found") from exc


@router.patch("/mentions/{mention_id}", response_model=MentionRead)
def update_mention(
    mention_id: UUID,
    payload: MentionUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> MentionRead:
    try:
        mention = MentionService(db).get_mention(mention_id)
        require_clinic_membership(db, current_user, mention.clinic_id)
        return MentionService(db).update_mention(mention_id=mention_id, data=payload)
    except MentionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mention not found") from exc


@router.delete("/mentions/{mention_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mention(
    mention_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    try:
        mention = MentionService(db).get_mention(mention_id)
        require_clinic_membership(db, current_user, mention.clinic_id)
        MentionService(db).delete_mention(mention_id)
    except MentionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mention not found") from exc
