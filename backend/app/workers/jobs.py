import logging

from app.integrations.ai.base import MentionAnalysisRequest
from app.integrations.email.base import EmailMessage
from app.modules.ai_analysis.service import AIAnalysisService
from app.modules.notifications.service import NotificationService

logger = logging.getLogger(__name__)


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
