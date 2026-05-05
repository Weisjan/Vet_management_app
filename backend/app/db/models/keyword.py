from typing import TYPE_CHECKING
from uuid import UUID

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import KeywordType, db_enum
from app.db.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.clinic import Clinic
    from app.db.models.user import User


class Keyword(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "keywords"
    __table_args__ = (
        Index("ix_keywords_clinic_id", "clinic_id"),
        Index("ix_keywords_clinic_value", "clinic_id", "value"),
    )

    clinic_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
    )
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[KeywordType] = mapped_column(
        db_enum(KeywordType, "keyword_type"),
        default=KeywordType.CUSTOM,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )

    clinic: Mapped["Clinic"] = relationship(back_populates="keywords")
    created_by_user: Mapped["User | None"] = relationship(
        back_populates="created_keywords",
        foreign_keys=[created_by_id],
    )
    versions: Mapped[list["KeywordVersion"]] = relationship(
        back_populates="keyword",
        cascade="all, delete-orphan",
    )


class KeywordVersion(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "keyword_versions"
    __table_args__ = (Index("ix_keyword_versions_keyword_id", "keyword_id"),)

    keyword_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("keywords.id", ondelete="CASCADE"),
        nullable=False,
    )
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str] = mapped_column(Text, nullable=False)
    changed_by_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    keyword: Mapped["Keyword"] = relationship(back_populates="versions")
    changed_by_user: Mapped["User | None"] = relationship(
        back_populates="keyword_versions",
        foreign_keys=[changed_by_id],
    )
