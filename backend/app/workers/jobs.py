import logging
from uuid import UUID

from app.db.models.enums import MentionCategory, RiskLevel, Sentiment
from app.db.models.mention import MentionAIAnalysis
from app.db.session import SessionLocal
from app.integrations.ai.base import MentionAnalysisRequest
from app.integrations.email.base import EmailMessage
from app.modules.ai_analysis.service import AIAnalysisService
from app.modules.notifications.service import NotificationService

logger = logging.getLogger(__name__)


def process_new_mention(mention_id: str) -> dict[str, str] | None:
    db = SessionLocal()
    try:
        from app.db.models.mention import Mention

        mention = db.get(Mention, UUID(mention_id))
        if mention is None:
            logger.warning("Mention not found for processing", extra={"mention_id": mention_id})
            return None

        result = AIAnalysisService().analyze_mention(
            MentionAnalysisRequest(
                content=mention.content,
                source=mention.source,
                clinic_name=mention.clinic.name if mention.clinic else None,
            )
        )

        existing = mention.ai_analysis
        if existing is None:
            analysis = MentionAIAnalysis(
                mention_id=mention.id,
                sentiment=Sentiment(result.sentiment),
                category=MentionCategory(result.category),
                risk_level=RiskLevel(result.risk_level),
                summary=result.summary,
                reasoning=result.reasoning,
                suggested_response=result.suggested_response,
                model_name="mock",
                model_version="mvp",
            )
            db.add(analysis)
        else:
            existing.sentiment = Sentiment(result.sentiment)
            existing.category = MentionCategory(result.category)
            existing.risk_level = RiskLevel(result.risk_level)
            existing.summary = result.summary
            existing.reasoning = result.reasoning
            existing.suggested_response = result.suggested_response
            existing.model_name = "mock"
            existing.model_version = "mvp"

        db.commit()
        logger.info("Mention processed", extra={"mention_id": mention_id, "risk_level": result.risk_level})
        return result.model_dump()
    finally:
        db.close()


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
