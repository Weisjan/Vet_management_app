from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import ReviewRequestEventType, ReviewRequestStatus, db_enum
from app.db.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.clinic import Clinic


class ReviewRequest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "review_requests"
    __table_args__ = (
        Index("ix_review_requests_clinic_id", "clinic_id"),
        Index("ix_review_requests_created_at", "created_at"),
    )

    clinic_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
    )
    customer_email: Mapped[str] = mapped_column(String(320), nullable=False)
    customer_name: Mapped[str | None] = mapped_column(String(255))
    visit_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    send_after: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reminder_after: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[ReviewRequestStatus] = mapped_column(
        db_enum(ReviewRequestStatus, "review_request_status"),
        default=ReviewRequestStatus.SCHEDULED,
        nullable=False,
    )
    review_link: Mapped[str] = mapped_column(String(1000), nullable=False)

    clinic: Mapped["Clinic"] = relationship(back_populates="review_requests")
    events: Mapped[list["ReviewRequestEvent"]] = relationship(
        back_populates="review_request",
        cascade="all, delete-orphan",
    )


class ReviewRequestEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "review_request_events"
    __table_args__ = (
        Index("ix_review_request_events_review_request_id", "review_request_id"),
        Index("ix_review_request_events_created_at", "created_at"),
    )

    review_request_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("review_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[ReviewRequestEventType] = mapped_column(
        db_enum(ReviewRequestEventType, "review_request_event_type"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    review_request: Mapped["ReviewRequest"] = relationship(back_populates="events")
