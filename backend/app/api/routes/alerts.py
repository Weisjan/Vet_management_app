from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import CurrentUser, DbSession, require_clinic_membership
from app.modules.alerts.schemas import AlertRead
from app.modules.alerts.service import AlertService, ClinicNotFoundForAlertError

router = APIRouter(tags=["alerts"])


@router.get("/clinics/{clinic_id}/alerts", response_model=list[AlertRead])
def list_alerts(
    clinic_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[AlertRead]:
    require_clinic_membership(db, current_user, clinic_id)
    try:
        return AlertService(db).list_alerts(clinic_id=clinic_id, offset=offset, limit=limit)
    except ClinicNotFoundForAlertError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found") from exc
