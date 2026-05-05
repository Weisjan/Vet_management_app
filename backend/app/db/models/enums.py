from enum import StrEnum
from typing import TypeVar

from sqlalchemy import Enum as SQLAlchemyEnum

EnumT = TypeVar("EnumT", bound=StrEnum)


def db_enum(enum_class: type[EnumT], name: str) -> SQLAlchemyEnum:
    return SQLAlchemyEnum(
        enum_class,
        name=name,
        values_callable=lambda enum_type: [item.value for item in enum_type],
    )


class AlertStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    ACKNOWLEDGED = "acknowledged"


class AlertType(StrEnum):
    NEW_MENTION = "new_mention"
    RISK_DETECTED = "risk_detected"


class ClinicMemberRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class KeywordType(StrEnum):
    CLINIC_NAME = "clinic_name"
    VET_NAME = "vet_name"
    ADDRESS = "address"
    PHONE = "phone"
    STAFF_NAME = "staff_name"
    NICKNAME = "nickname"
    MISSPELLING = "misspelling"
    LOCAL_REFERENCE = "local_reference"
    CUSTOM = "custom"


class MentionCategory(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    HARMFUL = "harmful"
    HATE = "hate"
    DEFAMATION_RISK = "defamation_risk"
    CRISIS_ESCALATION = "crisis_escalation"


class MentionStatus(StrEnum):
    NEW = "new"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"
    RESPONSE_DRAFTED = "response_drafted"
    RESOLVED = "resolved"


class NotificationChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class ReviewRequestEventType(StrEnum):
    SCHEDULED = "scheduled"
    SENT = "sent"
    OPENED = "opened"
    CLICKED = "clicked"
    REMINDED = "reminded"
    UNSUBSCRIBED = "unsubscribed"
    FAILED = "failed"


class ReviewRequestStatus(StrEnum):
    SCHEDULED = "scheduled"
    SENT = "sent"
    REMINDED = "reminded"
    UNSUBSCRIBED = "unsubscribed"
    FAILED = "failed"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Sentiment(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class SubscriptionPlan(StrEnum):
    BASIC = "basic"
    PRO = "pro"
    PREMIUM = "premium"


class SubscriptionStatus(StrEnum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"
