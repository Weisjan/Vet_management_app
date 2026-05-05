from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import DbSession, get_current_user_id
from app.modules.clinics.schemas import ClinicCreate, ClinicRead, ClinicUpdate
from app.modules.clinics.service import ClinicNotFoundError, ClinicService

router = APIRouter(prefix="/clinics", tags=["clinics"])


@router.get("", response_model=list[ClinicRead])
def list_clinics(
    db: DbSession,
    _: Annotated[None, Depends(get_current_user_id)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[ClinicRead]:
    return ClinicService(db).list_clinics(offset=offset, limit=limit)


@router.post("", response_model=ClinicRead, status_code=status.HTTP_201_CREATED)
def create_clinic(
    payload: ClinicCreate,
    db: DbSession,
    _: Annotated[None, Depends(get_current_user_id)],
) -> ClinicRead:
    return ClinicService(db).create_clinic(payload)


@router.get("/{clinic_id}", response_model=ClinicRead)
def get_clinic(
    clinic_id: UUID,
    db: DbSession,
    _: Annotated[None, Depends(get_current_user_id)],
) -> ClinicRead:
    try:
        return ClinicService(db).get_clinic(clinic_id)
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found") from exc


@router.patch("/{clinic_id}", response_model=ClinicRead)
def update_clinic(
    clinic_id: UUID,
    payload: ClinicUpdate,
    db: DbSession,
    _: Annotated[None, Depends(get_current_user_id)],
) -> ClinicRead:
    try:
        return ClinicService(db).update_clinic(clinic_id, payload)
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found") from exc


@router.delete("/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_clinic(
    clinic_id: UUID,
    db: DbSession,
    _: Annotated[None, Depends(get_current_user_id)],
) -> None:
    try:
        ClinicService(db).delete_clinic(clinic_id)
    except ClinicNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found") from exc
