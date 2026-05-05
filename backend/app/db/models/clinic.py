from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import ClinicMemberRole, db_enum
from app.db.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.alert import Alert
    from app.db.models.audit_log import AuditLog
    from app.db.models.keyword import Keyword
    from app.db.models.mention import Mention
    from app.db.models.notification import Notification
    from app.db.models.review_request import ReviewRequest
    from app.db.models.subscription import Subscription
    from app.db.models.unsubscribe import UnsubscribeToken
    from app.db.models.user import User


class Clinic(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "clinics"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500))
    phone: Mapped[str | None] = mapped_column(String(50))
    website: Mapped[str | None] = mapped_column(String(255))

    members: Mapped[list["ClinicMember"]] = relationship(
        back_populates="clinic",
        cascade="all, delete-orphan",
    )
    subscription: Mapped["Subscription | None"] = relationship(
        back_populates="clinic",
        uselist=False,
        cascade="all, delete-orphan",
    )
    keywords: Mapped[list["Keyword"]] = relationship(
        back_populates="clinic",
        cascade="all, delete-orphan",
    )
    mentions: Mapped[list["Mention"]] = relationship(back_populates="clinic")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="clinic")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="clinic")
    review_requests: Mapped[list["ReviewRequest"]] = relationship(back_populates="clinic")
    unsubscribe_tokens: Mapped[list["UnsubscribeToken"]] = relationship(back_populates="clinic")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="clinic")


class ClinicMember(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "clinic_members"
    __table_args__ = (
        UniqueConstraint("clinic_id", "user_id", name="uq_clinic_members_clinic_user"),
        Index("ix_clinic_members_clinic_id", "clinic_id"),
    )

    clinic_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[ClinicMemberRole] = mapped_column(
        db_enum(ClinicMemberRole, "clinic_member_role"),
        default=ClinicMemberRole.MEMBER,
        nullable=False,
    )

    clinic: Mapped["Clinic"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="clinic_memberships")
