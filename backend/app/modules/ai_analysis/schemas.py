from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.db.models.enums import MentionCategory, RiskLevel, Sentiment


class MentionAIAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    mention_id: UUID
    sentiment: Sentiment
    category: MentionCategory
    risk_level: RiskLevel
    summary: str
    reasoning: str
    suggested_response: str
    model_name: str | None
    model_version: str | None
    created_at: datetime
    updated_at: datetime
