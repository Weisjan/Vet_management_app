from app.integrations.ai import get_ai_provider
from app.integrations.ai.base import MentionAnalysisRequest, MentionAnalysisResult


class AIAnalysisService:
    def analyze_mention(self, request: MentionAnalysisRequest) -> MentionAnalysisResult:
        provider = get_ai_provider()
        return provider.analyze_mention(request)
