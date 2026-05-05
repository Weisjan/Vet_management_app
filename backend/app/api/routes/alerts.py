from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import DbSession, get_current_user_id
from app.modules.alerts.schemas import AlertRead
from app.modules.alerts.service import AlertService, ClinicNotFoundForAlertError

router = APIRouter(tags=["alerts"])


@router.get("/clinics/{clinic_id}/alerts", response_model=list[AlertRead])
def list_alerts(
    clinic_id: UUID,
    db: DbSession,
    _: Annotated[None, Depends(get_current_user_id)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[AlertRead]:
    try:
        return AlertService(db).list_alerts(clinic_id=clinic_id, offset=offset, limit=limit)
    except ClinicNotFoundForAlertError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found") from exc
