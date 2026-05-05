from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import NotificationChannel, NotificationStatus, db_enum
from app.db.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.clinic import Clinic
    from app.db.models.user import User


class Notification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_clinic_id", "clinic_id"),
        Index("ix_notifications_created_at", "created_at"),
    )

    clinic_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        db_enum(NotificationChannel, "notification_channel"),
        default=NotificationChannel.EMAIL,
        nullable=False,
    )
    recipient: Mapped[str] = mapped_column(String(320), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        db_enum(NotificationStatus, "notification_status"),
        default=NotificationStatus.PENDING,
        nullable=False,
    )
    provider_message_id: Mapped[str | None] = mapped_column(String(255))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    clinic: Mapped["Clinic"] = relationship(back_populates="notifications")
    user: Mapped["User | None"] = relationship(back_populates="notifications")
