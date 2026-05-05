from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.db.models.enums import AlertStatus, AlertType, RiskLevel


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    clinic_id: UUID
    mention_id: UUID | None
    type: AlertType
    risk_level: RiskLevel
    status: AlertStatus
    sent_at: datetime | None
    acknowledged_at: datetime | None
    acknowledged_by_id: UUID | None
    created_at: datetime
    updated_at: datetime
