import logging
from uuid import uuid4

from app.integrations.email.base import EmailMessage, EmailProvider, EmailSendResult

logger = logging.getLogger(__name__)


class MockEmailProvider(EmailProvider):
    def send_email(self, message: EmailMessage) -> EmailSendResult:
        message_id = f"mock-{uuid4()}"
        logger.info(
            "Mock email sent",
            extra={
                "message_id": message_id,
                "to": message.to,
                "subject": message.subject,
            },
        )
        return EmailSendResult(provider="mock", status="sent", message_id=message_id)
