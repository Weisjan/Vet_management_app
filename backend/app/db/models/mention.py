from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import MentionCategory, MentionStatus, RiskLevel, Sentiment, db_enum
from app.db.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.alert import Alert
    from app.db.models.clinic import Clinic


class Mention(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "mentions"
    __table_args__ = (
        Index("ix_mentions_clinic_id", "clinic_id"),
        Index("ix_mentions_source", "source"),
        Index("ix_mentions_created_at", "created_at"),
        Index("ix_mentions_clinic_created_at", "clinic_id", "created_at"),
        Index("ix_mentions_clinic_source", "clinic_id", "source"),
    )

    clinic_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1000))
    external_id: Mapped[str | None] = mapped_column(String(255))
    author_display_name: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evidence_snapshot: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[MentionStatus] = mapped_column(
        db_enum(MentionStatus, "mention_status"),
        default=MentionStatus.NEW,
        nullable=False,
    )

    clinic: Mapped["Clinic"] = relationship(back_populates="mentions")
    ai_analysis: Mapped["MentionAIAnalysis | None"] = relationship(
        back_populates="mention",
        uselist=False,
        cascade="all, delete-orphan",
    )
    alerts: Mapped[list["Alert"]] = relationship(back_populates="mention")


class MentionAIAnalysis(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "mention_ai_analyses"
    __table_args__ = (
        Index("ix_mention_ai_analyses_mention_id", "mention_id"),
        Index("ix_mention_ai_analyses_risk_level", "risk_level"),
        Index("ix_mention_ai_analyses_created_at", "created_at"),
    )

    mention_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("mentions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    sentiment: Mapped[Sentiment] = mapped_column(
        db_enum(Sentiment, "sentiment"),
        nullable=False,
    )
    category: Mapped[MentionCategory] = mapped_column(
        db_enum(MentionCategory, "mention_category"),
        nullable=False,
    )
    risk_level: Mapped[RiskLevel] = mapped_column(
        db_enum(RiskLevel, "risk_level"),
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_response: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(100))
    model_version: Mapped[str | None] = mapped_column(String(100))

    mention: Mapped["Mention"] = relationship(back_populates="ai_analysis")
