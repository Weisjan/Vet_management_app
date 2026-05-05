from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import UserRole, db_enum
from app.db.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.alert import Alert
    from app.db.models.audit_log import AuditLog
    from app.db.models.clinic import ClinicMember
    from app.db.models.keyword import Keyword, KeywordVersion
    from app.db.models.notification import Notification


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        db_enum(UserRole, "user_role"),
        default=UserRole.USER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    clinic_memberships: Mapped[list["ClinicMember"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    created_keywords: Mapped[list["Keyword"]] = relationship(
        back_populates="created_by_user",
        foreign_keys="Keyword.created_by_id",
    )
    keyword_versions: Mapped[list["KeywordVersion"]] = relationship(
        back_populates="changed_by_user",
        foreign_keys="KeywordVersion.changed_by_id",
    )
    acknowledged_alerts: Mapped[list["Alert"]] = relationship(
        back_populates="acknowledged_by_user",
        foreign_keys="Alert.acknowledged_by_id",
    )
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")
