from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, Field


class MentionAnalysisRequest(BaseModel):
    content: str
    source: str | None = None
    clinic_name: str | None = None
    matched_keywords: list[str] = Field(default_factory=list)


class MentionAnalysisResult(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    category: Literal[
        "positive",
        "neutral",
        "negative",
        "harmful",
        "hate",
        "defamation_risk",
        "crisis_escalation",
    ]
    risk_level: Literal["low", "medium", "high"]
    summary: str
    reasoning: str
    suggested_response: str


class AIProvider(ABC):
    @abstractmethod
    def analyze_mention(self, request: MentionAnalysisRequest) -> MentionAnalysisResult:
        raise NotImplementedError
