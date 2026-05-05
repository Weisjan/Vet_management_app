from app.core.config import settings
from app.integrations.email.base import EmailProvider
from app.integrations.email.mock_provider import MockEmailProvider


def get_email_provider() -> EmailProvider:
    if settings.email_provider == "mock":
        return MockEmailProvider()

    raise ValueError(f"Unsupported email provider: {settings.email_provider}")
