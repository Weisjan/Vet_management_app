from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models.enums import MentionStatus


class MentionBase(BaseModel):
    source: str = Field(min_length=1, max_length=100)
    source_url: str | None = Field(default=None, max_length=1000)
    content: str = Field(min_length=1)
    author_display_name: str | None = Field(default=None, max_length=255)
    published_at: datetime | None = None

    @field_validator("source", "content", mode="before")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("Value must not be blank")
            return stripped
        return value

    @field_validator("source_url", "author_display_name", mode="before")
    @classmethod
    def strip_optional_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value


class MentionCreate(MentionBase):
    pass


class MentionUpdate(BaseModel):
    source: str | None = Field(default=None, min_length=1, max_length=100)
    source_url: str | None = Field(default=None, max_length=1000)
    content: str | None = Field(default=None, min_length=1)
    author_display_name: str | None = Field(default=None, max_length=255)
    published_at: datetime | None = None
    status: MentionStatus | None = None

    @field_validator("source", "content", mode="before")
    @classmethod
    def strip_required_update_strings(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("Value must not be null")
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("Value must not be blank")
            return stripped
        return value

    @field_validator("source_url", "author_display_name", mode="before")
    @classmethod
    def strip_optional_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value


class MentionRead(MentionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    clinic_id: UUID
    status: MentionStatus
    detected_at: datetime
    created_at: datetime
    updated_at: datetime
