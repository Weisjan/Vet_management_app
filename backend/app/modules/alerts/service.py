from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.alert import Alert
from app.db.models.clinic import Clinic


class AlertNotFoundError(Exception):
    pass


class ClinicNotFoundForAlertError(Exception):
    pass


class AlertService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_alerts(
        self,
        *,
        clinic_id: UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Alert]:
        self._ensure_clinic_exists(clinic_id)
        statement = (
            select(Alert)
            .where(Alert.clinic_id == clinic_id)
            .order_by(Alert.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement))

    def _ensure_clinic_exists(self, clinic_id: UUID) -> None:
        if self.db.get(Clinic, clinic_id) is None:
            raise ClinicNotFoundForAlertError
