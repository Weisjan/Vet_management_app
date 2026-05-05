from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.clinic import Clinic


class UnsubscribeToken(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "unsubscribe_tokens"
    __table_args__ = (
        UniqueConstraint("clinic_id", "email", name="uq_unsubscribe_tokens_clinic_email"),
        Index("ix_unsubscribe_tokens_clinic_id", "clinic_id"),
    )

    clinic_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    unsubscribed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    clinic: Mapped["Clinic"] = relationship(back_populates="unsubscribe_tokens")
