from app.integrations.email import get_email_provider
from app.integrations.email.base import EmailMessage, EmailSendResult


class NotificationService:
    def send_email(self, message: EmailMessage) -> EmailSendResult:
        provider = get_email_provider()
        return provider.send_email(message)
