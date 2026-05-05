"""create mvp schema

Revision ID: 202605060001
Revises:
Create Date: 2026-05-06 00:01:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "202605060001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


UUID = postgresql.UUID(as_uuid=True)

user_role = postgresql.ENUM("user", "admin", name="user_role", create_type=False)
clinic_member_role = postgresql.ENUM(
    "owner", "admin", "member", name="clinic_member_role", create_type=False
)
subscription_plan = postgresql.ENUM(
    "basic", "pro", "premium", name="subscription_plan", create_type=False
)
subscription_status = postgresql.ENUM(
    "trialing", "active", "past_due", "canceled", name="subscription_status", create_type=False
)
keyword_type = postgresql.ENUM(
    "clinic_name",
    "vet_name",
    "address",
    "phone",
    "staff_name",
    "nickname",
    "misspelling",
    "local_reference",
    "custom",
    name="keyword_type",
    create_type=False,
)
mention_status = postgresql.ENUM(
    "new", "reviewed", "dismissed", "response_drafted", "resolved", name="mention_status", create_type=False
)
sentiment = postgresql.ENUM("positive", "neutral", "negative", name="sentiment", create_type=False)
mention_category = postgresql.ENUM(
    "positive",
    "neutral",
    "negative",
    "harmful",
    "hate",
    "defamation_risk",
    "crisis_escalation",
    name="mention_category",
    create_type=False,
)
risk_level = postgresql.ENUM("low", "medium", "high", name="risk_level", create_type=False)
alert_type = postgresql.ENUM("new_mention", "risk_detected", name="alert_type", create_type=False)
alert_status = postgresql.ENUM(
    "pending", "sent", "failed", "acknowledged", name="alert_status", create_type=False
)
notification_channel = postgresql.ENUM(
    "email", "sms", "in_app", name="notification_channel", create_type=False
)
notification_status = postgresql.ENUM(
    "pending", "sent", "failed", name="notification_status", create_type=False
)
review_request_status = postgresql.ENUM(
    "scheduled", "sent", "reminded", "unsubscribed", "failed",
    name="review_request_status",
    create_type=False,
)
review_request_event_type = postgresql.ENUM(
    "scheduled",
    "sent",
    "opened",
    "clicked",
    "reminded",
    "unsubscribed",
    "failed",
    name="review_request_event_type",
    create_type=False,
)


def _create_enum_types() -> None:
    bind = op.get_bind()
    for enum_type in (
        user_role,
        clinic_member_role,
        subscription_plan,
        subscription_status,
        keyword_type,
        mention_status,
        sentiment,
        mention_category,
        risk_level,
        alert_type,
        alert_status,
        notification_channel,
        notification_status,
        review_request_status,
        review_request_event_type,
    ):
        enum_type.create(bind, checkfirst=True)


def _drop_enum_types() -> None:
    bind = op.get_bind()
    for enum_type in (
        review_request_event_type,
        review_request_status,
        notification_status,
        notification_channel,
        alert_status,
        alert_type,
        risk_level,
        mention_category,
        sentiment,
        mention_status,
        keyword_type,
        subscription_status,
        subscription_plan,
        clinic_member_role,
        user_role,
    ):
        enum_type.drop(bind, checkfirst=True)


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    _create_enum_types()

    op.create_table(
        "users",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, server_default="user", nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", UUID, nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)

    op.create_table(
        "clinics",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("id", UUID, nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_clinics")),
    )

    op.create_table(
        "clinic_members",
        sa.Column("clinic_id", UUID, nullable=False),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("role", clinic_member_role, server_default="member", nullable=False),
        sa.Column("id", UUID, nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"], ondelete="CASCADE", name=op.f("fk_clinic_members_clinic_id_clinics")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("fk_clinic_members_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_clinic_members")),
        sa.UniqueConstraint("clinic_id", "user_id", name="uq_clinic_members_clinic_user"),
    )
    op.create_index("ix_clinic_members_clinic_id", "clinic_members", ["clinic_id"], unique=False)

    op.create_table(
        "subscriptions",
        sa.Column("clinic_id", UUID, nullable=False),
        sa.Column("plan", subscription_plan, server_default="basic", nullable=False),
        sa.Column("status", subscription_status, server_default="trialing", nullable=False),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", UUID, nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"], ondelete="CASCADE", name=op.f("fk_subscriptions_clinic_id_clinics")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscriptions")),
        sa.UniqueConstraint("clinic_id", name=op.f("uq_subscriptions_clinic_id")),
    )
    op.create_index("ix_subscriptions_clinic_id", "subscriptions", ["clinic_id"], unique=False)

    op.create_table(
        "keywords",
        sa.Column("clinic_id", UUID, nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("type", keyword_type, server_default="custom", nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", UUID, nullable=True),
        sa.Column("id", UUID, nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"], ondelete="CASCADE", name=op.f("fk_keywords_clinic_id_clinics")),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL", name=op.f("fk_keywords_created_by_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_keywords")),
    )
    op.create_index("ix_keywords_clinic_id", "keywords", ["clinic_id"], unique=False)
    op.create_index("ix_keywords_clinic_value", "keywords", ["clinic_id", "value"], unique=False)

    op.create_table(
        "keyword_versions",
        sa.Column("keyword_id", UUID, nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=False),
        sa.Column("changed_by_id", UUID, nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("id", UUID, nullable=False),
        sa.ForeignKeyConstraint(["changed_by_id"], ["users.id"], ondelete="SET NULL", name=op.f("fk_keyword_versions_changed_by_id_users")),
        sa.ForeignKeyConstraint(["keyword_id"], ["keywords.id"], ondelete="CASCADE", name=op.f("fk_keyword_versions_keyword_id_keywords")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_keyword_versions")),
    )
    op.create_index("ix_keyword_versions_keyword_id", "keyword_versions", ["keyword_id"], unique=False)

    op.create_table(
        "mentions",
        sa.Column("clinic_id", UUID, nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("author_display_name", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evidence_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", mention_status, server_default="new", nullable=False),
        sa.Column("id", UUID, nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"], ondelete="CASCADE", name=op.f("fk_mentions_clinic_id_clinics")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mentions")),
    )
    op.create_index("ix_mentions_clinic_created_at", "mentions", ["clinic_id", "created_at"], unique=False)
    op.create_index("ix_mentions_clinic_id", "mentions", ["clinic_id"], unique=False)
    op.create_index("ix_mentions_clinic_source", "mentions", ["clinic_id", "source"], unique=False)
    op.create_index("ix_mentions_created_at", "mentions", ["created_at"], unique=False)
    op.create_index("ix_mentions_source", "mentions", ["source"], unique=False)

    op.create_table(
        "mention_ai_analyses",
        sa.Column("mention_id", UUID, nullable=False),
        sa.Column("sentiment", sentiment, nullable=False),
        sa.Column("category", mention_category, nullable=False),
        sa.Column("risk_level", risk_level, nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("suggested_response", sa.Text(), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        sa.Column("model_version", sa.String(length=100), nullable=True),
        sa.Column("id", UUID, nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["mention_id"], ["mentions.id"], ondelete="CASCADE", name=op.f("fk_mention_ai_analyses_mention_id_mentions")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mention_ai_analyses")),
        sa.UniqueConstraint("mention_id", name=op.f("uq_mention_ai_analyses_mention_id")),
    )
    op.create_index("ix_mention_ai_analyses_created_at", "mention_ai_analyses", ["created_at"], unique=False)
    op.create_index("ix_mention_ai_analyses_mention_id", "mention_ai_analyses", ["mention_id"], unique=False)
    op.create_index("ix_mention_ai_analyses_risk_level", "mention_ai_analyses", ["risk_level"], unique=False)

    op.create_table(
        "alerts",
        sa.Column("clinic_id", UUID, nullable=False),
        sa.Column("mention_id", UUID, nullable=True),
        sa.Column("type", alert_type, nullable=False),
        sa.Column("risk_level", risk_level, nullable=False),
        sa.Column("status", alert_status, server_default="pending", nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by_id", UUID, nullable=True),
        sa.Column("id", UUID, nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["acknowledged_by_id"], ["users.id"], ondelete="SET NULL", name=op.f("fk_alerts_acknowledged_by_id_users")),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"], ondelete="CASCADE", name=op.f("fk_alerts_clinic_id_clinics")),
        sa.ForeignKeyConstraint(["mention_id"], ["mentions.id"], ondelete="SET NULL", name=op.f("fk_alerts_mention_id_mentions")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_alerts")),
    )
    op.create_index("ix_alerts_clinic_id", "alerts", ["clinic_id"], unique=False)
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"], unique=False)
    op.create_index("ix_alerts_mention_id", "alerts", ["mention_id"], unique=False)
    op.create_index("ix_alerts_risk_level", "alerts", ["risk_level"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("clinic_id", UUID, nullable=False),
        sa.Column("user_id", UUID, nullable=True),
        sa.Column("channel", notification_channel, server_default="email", nullable=False),
        sa.Column("recipient", sa.String(length=320), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", notification_status, server_default="pending", nullable=False),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", UUID, nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"], ondelete="CASCADE", name=op.f("fk_notifications_clinic_id_clinics")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL", name=op.f("fk_notifications_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
    )
    op.create_index("ix_notifications_clinic_id", "notifications", ["clinic_id"], unique=False)
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"], unique=False)

    op.create_table(
        "review_requests",
        sa.Column("clinic_id", UUID, nullable=False),
        sa.Column("customer_email", sa.String(length=320), nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("visit_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("send_after", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reminder_after", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", review_request_status, server_default="scheduled", nullable=False),
        sa.Column("review_link", sa.String(length=1000), nullable=False),
        sa.Column("id", UUID, nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"], ondelete="CASCADE", name=op.f("fk_review_requests_clinic_id_clinics")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_review_requests")),
    )
    op.create_index("ix_review_requests_clinic_id", "review_requests", ["clinic_id"], unique=False)
    op.create_index("ix_review_requests_created_at", "review_requests", ["created_at"], unique=False)

    op.create_table(
        "review_request_events",
        sa.Column("review_request_id", UUID, nullable=False),
        sa.Column("event_type", review_request_event_type, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("id", UUID, nullable=False),
        sa.ForeignKeyConstraint(["review_request_id"], ["review_requests.id"], ondelete="CASCADE", name=op.f("fk_review_request_events_review_request_id_review_requests")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_review_request_events")),
    )
    op.create_index("ix_review_request_events_created_at", "review_request_events", ["created_at"], unique=False)
    op.create_index("ix_review_request_events_review_request_id", "review_request_events", ["review_request_id"], unique=False)

    op.create_table(
        "unsubscribe_tokens",
        sa.Column("clinic_id", UUID, nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("unsubscribed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", UUID, nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"], ondelete="CASCADE", name=op.f("fk_unsubscribe_tokens_clinic_id_clinics")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_unsubscribe_tokens")),
        sa.UniqueConstraint("clinic_id", "email", name="uq_unsubscribe_tokens_clinic_email"),
    )
    op.create_index("ix_unsubscribe_tokens_clinic_id", "unsubscribe_tokens", ["clinic_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("clinic_id", UUID, nullable=True),
        sa.Column("user_id", UUID, nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=True),
        sa.Column("entity_id", UUID, nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", UUID, nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"], ondelete="SET NULL", name=op.f("fk_audit_logs_clinic_id_clinics")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL", name=op.f("fk_audit_logs_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )
    op.create_index("ix_audit_logs_clinic_id", "audit_logs", ["clinic_id"], unique=False)
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_clinic_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_unsubscribe_tokens_clinic_id", table_name="unsubscribe_tokens")
    op.drop_table("unsubscribe_tokens")
    op.drop_index("ix_review_request_events_review_request_id", table_name="review_request_events")
    op.drop_index("ix_review_request_events_created_at", table_name="review_request_events")
    op.drop_table("review_request_events")
    op.drop_index("ix_review_requests_created_at", table_name="review_requests")
    op.drop_index("ix_review_requests_clinic_id", table_name="review_requests")
    op.drop_table("review_requests")
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_index("ix_notifications_clinic_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_alerts_risk_level", table_name="alerts")
    op.drop_index("ix_alerts_mention_id", table_name="alerts")
    op.drop_index("ix_alerts_created_at", table_name="alerts")
    op.drop_index("ix_alerts_clinic_id", table_name="alerts")
    op.drop_table("alerts")
    op.drop_index("ix_mention_ai_analyses_risk_level", table_name="mention_ai_analyses")
    op.drop_index("ix_mention_ai_analyses_mention_id", table_name="mention_ai_analyses")
    op.drop_index("ix_mention_ai_analyses_created_at", table_name="mention_ai_analyses")
    op.drop_table("mention_ai_analyses")
    op.drop_index("ix_mentions_source", table_name="mentions")
    op.drop_index("ix_mentions_created_at", table_name="mentions")
    op.drop_index("ix_mentions_clinic_source", table_name="mentions")
    op.drop_index("ix_mentions_clinic_id", table_name="mentions")
    op.drop_index("ix_mentions_clinic_created_at", table_name="mentions")
    op.drop_table("mentions")
    op.drop_index("ix_keyword_versions_keyword_id", table_name="keyword_versions")
    op.drop_table("keyword_versions")
    op.drop_index("ix_keywords_clinic_value", table_name="keywords")
    op.drop_index("ix_keywords_clinic_id", table_name="keywords")
    op.drop_table("keywords")
    op.drop_index("ix_subscriptions_clinic_id", table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_index("ix_clinic_members_clinic_id", table_name="clinic_members")
    op.drop_table("clinic_members")
    op.drop_table("clinics")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    _drop_enum_types()
