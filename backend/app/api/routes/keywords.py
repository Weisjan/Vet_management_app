from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import CurrentUser, DbSession, require_clinic_membership
from app.modules.keywords.schemas import KeywordCreate, KeywordRead, KeywordUpdate
from app.modules.keywords.service import (
    ClinicNotFoundForKeywordError,
    KeywordConflictError,
    KeywordNotFoundError,
    KeywordService,
)

router = APIRouter(tags=["keywords"])


@router.get("/clinics/{clinic_id}/keywords", response_model=list[KeywordRead])
def list_keywords(
    clinic_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[KeywordRead]:
    require_clinic_membership(db, current_user, clinic_id)
    try:
        return KeywordService(db).list_keywords(clinic_id=clinic_id, offset=offset, limit=limit)
    except ClinicNotFoundForKeywordError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found") from exc


@router.post(
    "/clinics/{clinic_id}/keywords",
    response_model=KeywordRead,
    status_code=status.HTTP_201_CREATED,
)
def create_keyword(
    clinic_id: UUID,
    payload: KeywordCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> KeywordRead:
    require_clinic_membership(db, current_user, clinic_id)
    try:
        return KeywordService(db).create_keyword(
            clinic_id=clinic_id,
            data=payload,
            created_by_id=current_user.id,
        )
    except ClinicNotFoundForKeywordError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found") from exc
    except KeywordConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Keyword already exists for this clinic",
        ) from exc


@router.get("/keywords/{keyword_id}", response_model=KeywordRead)
def get_keyword(
    keyword_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> KeywordRead:
    try:
        keyword = KeywordService(db).get_keyword(keyword_id)
        require_clinic_membership(db, current_user, keyword.clinic_id)
        return keyword
    except KeywordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keyword not found") from exc


@router.patch("/keywords/{keyword_id}", response_model=KeywordRead)
def update_keyword(
    keyword_id: UUID,
    payload: KeywordUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> KeywordRead:
    try:
        keyword = KeywordService(db).get_keyword(keyword_id)
        require_clinic_membership(db, current_user, keyword.clinic_id)
        return KeywordService(db).update_keyword(
            keyword_id=keyword_id,
            data=payload,
            changed_by_id=current_user.id,
        )
    except KeywordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keyword not found") from exc
    except KeywordConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Keyword already exists for this clinic",
        ) from exc


@router.delete("/keywords/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_keyword(
    keyword_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    try:
        keyword = KeywordService(db).get_keyword(keyword_id)
        require_clinic_membership(db, current_user, keyword.clinic_id)
        KeywordService(db).delete_keyword(keyword_id)
    except KeywordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keyword not found") from exc
