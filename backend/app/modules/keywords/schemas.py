from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models.enums import KeywordType


class KeywordBase(BaseModel):
    value: str = Field(min_length=1, max_length=255)
    type: KeywordType = KeywordType.CUSTOM
    is_active: bool = True

    @field_validator("value", mode="before")
    @classmethod
    def strip_value(cls, value: str) -> str:
        if value is None:
            raise ValueError("Keyword value must not be null")
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("Keyword value must not be blank")
            return stripped
        return value


class KeywordCreate(KeywordBase):
    pass


class KeywordUpdate(BaseModel):
    value: str | None = Field(default=None, min_length=1, max_length=255)
    type: KeywordType | None = None
    is_active: bool | None = None

    @field_validator("value", mode="before")
    @classmethod
    def strip_value(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("Keyword value must not be null")
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("Keyword value must not be blank")
            return stripped
        return value


class KeywordRead(KeywordBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    clinic_id: UUID
    created_by_id: UUID | None
    created_at: datetime
    updated_at: datetime
