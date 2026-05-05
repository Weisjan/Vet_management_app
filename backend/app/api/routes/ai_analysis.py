from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.dependencies import DbSession, get_current_user_id
from app.db.models.mention import Mention, MentionAIAnalysis
from app.modules.ai_analysis.schemas import MentionAIAnalysisRead

router = APIRouter(tags=["ai-analysis"])


@router.get("/mentions/{mention_id}/ai-analysis", response_model=MentionAIAnalysisRead)
def get_mention_ai_analysis(
    mention_id: UUID,
    db: DbSession,
    _: Annotated[None, Depends(get_current_user_id)],
) -> MentionAIAnalysisRead:
    mention = db.get(Mention, mention_id)
    if mention is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mention not found")

    analysis = db.scalars(
        select(MentionAIAnalysis).where(MentionAIAnalysis.mention_id == mention_id)
    ).one_or_none()
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI analysis not found")

    return analysis
