from abc import ABC, abstractmethod

from pydantic import BaseModel


class EmailMessage(BaseModel):
    to: str
    subject: str
    body: str


class EmailSendResult(BaseModel):
    provider: str
    status: str
    message_id: str | None = None


class EmailProvider(ABC):
    @abstractmethod
    def send_email(self, message: EmailMessage) -> EmailSendResult:
        raise NotImplementedError
