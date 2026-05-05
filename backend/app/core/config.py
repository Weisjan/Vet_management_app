from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Vet Reputation AI"
    app_env: str = "local"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+psycopg://vet_reputation:vet_reputation@localhost:5432/vet_reputation"
    )
    redis_url: str = "redis://localhost:6379/0"
    rq_queues: str = "default,ai,notifications,review_requests"

    ai_provider: Literal["mock"] = "mock"
    email_provider: Literal["mock"] = "mock"
    default_from_email: str = "no-reply@example.local"

    log_level: str = "INFO"

    @property
    def queue_names(self) -> list[str]:
        return [queue.strip() for queue in self.rq_queues.split(",") if queue.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
