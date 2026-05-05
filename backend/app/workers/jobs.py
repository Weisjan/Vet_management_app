import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.alert import Alert
from app.db.models.enums import (
    AlertStatus,
    AlertType,
    MentionCategory,
    NotificationChannel,
    NotificationStatus,
    RiskLevel,
    Sentiment,
)
from app.db.models.mention import Mention, MentionAIAnalysis
from app.db.models.notification import Notification
from app.db.session import SessionLocal
from app.integrations.ai.base import MentionAnalysisRequest
from app.integrations.email.base import EmailMessage
from app.modules.ai_analysis.service import AIAnalysisService
from app.modules.notifications.service import NotificationService

logger = logging.getLogger(__name__)


def process_new_mention(mention_id: str) -> dict[str, str] | None:
    db = SessionLocal()
    try:
        return process_new_mention_with_session(db, UUID(mention_id))
    finally:
        db.close()


def process_new_mention_with_session(db: Session, mention_id: UUID | str) -> dict[str, str] | None:
    mention_uuid = UUID(mention_id) if isinstance(mention_id, str) else mention_id
    mention = db.get(Mention, mention_uuid)
    if mention is None:
        logger.warning("Mention not found for processing", extra={"mention_id": str(mention_uuid)})
        return None

    result = AIAnalysisService().analyze_mention(
        MentionAnalysisRequest(
            content=mention.content,
            source=mention.source,
            clinic_name=mention.clinic.name if mention.clinic else None,
        )
    )

    risk_level = RiskLevel(result.risk_level)
    existing = mention.ai_analysis
    if existing is None:
        analysis = MentionAIAnalysis(
            mention_id=mention.id,
            sentiment=Sentiment(result.sentiment),
            category=MentionCategory(result.category),
            risk_level=risk_level,
            summary=result.summary,
            reasoning=result.reasoning,
            suggested_response=result.suggested_response,
            model_name=settings.ai_provider,
            model_version="mvp",
        )
        db.add(analysis)
    else:
        existing.sentiment = Sentiment(result.sentiment)
        existing.category = MentionCategory(result.category)
        existing.risk_level = risk_level
        existing.summary = result.summary
        existing.reasoning = result.reasoning
        existing.suggested_response = result.suggested_response
        existing.model_name = settings.ai_provider
        existing.model_version = "mvp"

    if risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH}:
        _ensure_alert_and_notification(db, mention, risk_level)

    db.commit()
    logger.info(
        "Mention processed",
        extra={"mention_id": str(mention_uuid), "risk_level": result.risk_level},
    )
    return result.model_dump()


def _ensure_alert_and_notification(db: Session, mention: Mention, risk_level: RiskLevel) -> None:
    statement = select(Alert).where(
        Alert.mention_id == mention.id,
        Alert.type == AlertType.RISK_DETECTED,
    )
    alert = db.scalars(statement).first()

    if alert is None:
        alert = Alert(
            clinic_id=mention.clinic_id,
            mention_id=mention.id,
            type=AlertType.RISK_DETECTED,
            risk_level=risk_level,
            status=AlertStatus.PENDING,
        )
        db.add(alert)
        db.flush()
        _create_alert_notification(db, mention, alert)
    else:
        alert.risk_level = risk_level


def _create_alert_notification(db: Session, mention: Mention, alert: Alert) -> None:
    subject = f"New {alert.risk_level.value.upper()} risk mention requires review"
    body = (
        f"A {alert.risk_level.value} risk mention was detected from {mention.source}. "
        f"Mention ID: {mention.id}. Please review it in the dashboard."
    )
    db.add(
        Notification(
            clinic_id=mention.clinic_id,
            user_id=None,
            channel=NotificationChannel.EMAIL,
            recipient="clinic-alerts@example.local",
            subject=subject,
            body=body,
            status=NotificationStatus.PENDING,
        )
    )


def analyze_mock_mention(content: str) -> dict[str, str]:
    result = AIAnalysisService().analyze_mention(
        MentionAnalysisRequest(content=content, source="mock")
    )
    logger.info("Mock mention analyzed", extra={"risk_level": result.risk_level})
    return result.model_dump()


def send_mock_email(to: str, subject: str, body: str) -> dict[str, str | None]:
    result = NotificationService().send_email(
        EmailMessage(to=to, subject=subject, body=body)
    )
    return result.model_dump()
