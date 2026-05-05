from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import AlertStatus, AlertType, RiskLevel, db_enum
from app.db.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.clinic import Clinic
    from app.db.models.mention import Mention
    from app.db.models.user import User


class Alert(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("ix_alerts_clinic_id", "clinic_id"),
        Index("ix_alerts_mention_id", "mention_id"),
        Index("ix_alerts_risk_level", "risk_level"),
        Index("ix_alerts_created_at", "created_at"),
    )

    clinic_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
    )
    mention_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("mentions.id", ondelete="SET NULL"),
    )
    type: Mapped[AlertType] = mapped_column(db_enum(AlertType, "alert_type"), nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(db_enum(RiskLevel, "risk_level"), nullable=False)
    status: Mapped[AlertStatus] = mapped_column(
        db_enum(AlertStatus, "alert_status"),
        default=AlertStatus.PENDING,
        nullable=False,
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    acknowledged_by_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )

    clinic: Mapped["Clinic"] = relationship(back_populates="alerts")
    mention: Mapped["Mention | None"] = relationship(back_populates="alerts")
    acknowledged_by_user: Mapped["User | None"] = relationship(
        back_populates="acknowledged_alerts",
        foreign_keys=[acknowledged_by_id],
    )
