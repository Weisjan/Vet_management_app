from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DbSession, require_clinic_membership
from app.db.models.mention import Mention, MentionAIAnalysis
from app.modules.ai_analysis.schemas import MentionAIAnalysisRead

router = APIRouter(tags=["ai-analysis"])


@router.get("/mentions/{mention_id}/ai-analysis", response_model=MentionAIAnalysisRead)
def get_mention_ai_analysis(
    mention_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> MentionAIAnalysisRead:
    mention = db.get(Mention, mention_id)
    if mention is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mention not found")
    require_clinic_membership(db, current_user, mention.clinic_id)

    analysis = db.scalars(
        select(MentionAIAnalysis).where(MentionAIAnalysis.mention_id == mention_id)
    ).one_or_none()
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI analysis not found")

    return analysis
