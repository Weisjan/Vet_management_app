from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import CurrentUser, DbSession, require_clinic_membership
from app.modules.clinics.schemas import ClinicCreate, ClinicRead, ClinicUpdate
from app.modules.clinics.service import ClinicNotFoundError, ClinicService

router = APIRouter(prefix="/clinics", tags=["clinics"])


@router.get("", response_model=list[ClinicRead])
def list_clinics(
    db: DbSession,
    current_user: CurrentUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[ClinicRead]:
    return ClinicService(db).list_clinics(user_id=current_user.id, offset=offset, limit=limit)


@router.post("", response_model=ClinicRead, status_code=status.HTTP_201_CREATED)
def create_clinic(
    payload: ClinicCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ClinicRead:
    return ClinicService(db).create_clinic(payload, owner_id=current_user.id)


@router.get("/{clinic_id}", response_model=ClinicRead)
def get_clinic(
    clinic_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ClinicRead:
    require_clinic_membership(db, current_user, clinic_id)
    try:
        return ClinicService(db).get_clinic(clinic_id)
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found") from exc


@router.patch("/{clinic_id}", response_model=ClinicRead)
def update_clinic(
    clinic_id: UUID,
    payload: ClinicUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ClinicRead:
    require_clinic_membership(db, current_user, clinic_id)
    try:
        return ClinicService(db).update_clinic(clinic_id, payload)
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found") from exc


@router.delete("/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_clinic(
    clinic_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    require_clinic_membership(db, current_user, clinic_id)
    try:
        ClinicService(db).delete_clinic(clinic_id)
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found") from exc
