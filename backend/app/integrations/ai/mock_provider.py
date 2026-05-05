from app.integrations.ai.base import (
    AIProvider,
    MentionAnalysisRequest,
    MentionAnalysisResult,
)


class MockAIProvider(AIProvider):
    def analyze_mention(self, request: MentionAnalysisRequest) -> MentionAnalysisResult:
        content = request.content.lower()

        if any(term in content for term in ["fraud", "negligence", "lawsuit", "abuse"]):
            return MentionAnalysisResult(
                sentiment="negative",
                category="defamation_risk",
                risk_level="high",
                summary="Potentially serious allegation detected.",
                reasoning="The mention contains language that may create legal or reputation risk.",
                suggested_response=(
                    "Thank you for sharing your concerns. Please contact the clinic directly "
                    "so the team can review the matter appropriately."
                ),
            )

        if any(term in content for term in ["bad", "angry", "rude", "expensive"]):
            return MentionAnalysisResult(
                sentiment="negative",
                category="negative",
                risk_level="medium",
                summary="Negative customer experience detected.",
                reasoning="The mention expresses dissatisfaction and should be reviewed by a human.",
                suggested_response=(
                    "Thank you for your feedback. We are sorry to hear about your experience "
                    "and invite you to contact us directly so we can understand the situation."
                ),
            )

        if any(term in content for term in ["great", "thank", "excellent", "kind"]):
            return MentionAnalysisResult(
                sentiment="positive",
                category="positive",
                risk_level="low",
                summary="Positive feedback detected.",
                reasoning="The mention expresses appreciation or satisfaction.",
                suggested_response="Thank you for your kind feedback. We appreciate your trust.",
            )

        return MentionAnalysisResult(
            sentiment="neutral",
            category="neutral",
            risk_level="low",
            summary="Neutral mention detected.",
            reasoning="The mention does not contain obvious positive or negative risk indicators.",
            suggested_response="Thank you for your message.",
        )
