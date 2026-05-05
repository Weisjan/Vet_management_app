from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClinicBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=50)
    website: str | None = Field(default=None, max_length=255)

    @field_validator("name", mode="before")
    @classmethod
    def strip_required_name(cls, value: str) -> str:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("Name must not be blank")
            return stripped
        return value

    @field_validator("address", "phone", "website", mode="before")
    @classmethod
    def strip_optional_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value


class ClinicCreate(ClinicBase):
    pass


class ClinicUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=50)
    website: str | None = Field(default=None, max_length=255)

    @field_validator("name", mode="before")
    @classmethod
    def strip_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("Name must not be null")
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("Name must not be blank")
            return stripped
        return value

    @field_validator("address", "phone", "website", mode="before")
    @classmethod
    def strip_optional_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value


class ClinicRead(ClinicBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
