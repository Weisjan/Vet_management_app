from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.clinic import Clinic
from app.db.models.mention import Mention
from app.modules.mentions.schemas import MentionCreate, MentionUpdate


class MentionNotFoundError(Exception):
    pass


class ClinicNotFoundForMentionError(Exception):
    pass


class MentionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_mentions(
        self,
        *,
        clinic_id: UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Mention]:
        self._ensure_clinic_exists(clinic_id)
        statement = (
            select(Mention)
            .where(Mention.clinic_id == clinic_id)
            .order_by(Mention.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement))

    def get_mention(self, mention_id: UUID) -> Mention:
        mention = self.db.get(Mention, mention_id)
        if mention is None:
            raise MentionNotFoundError
        return mention

    def create_mention(self, *, clinic_id: UUID, data: MentionCreate) -> Mention:
        self._ensure_clinic_exists(clinic_id)
        mention = Mention(
            clinic_id=clinic_id,
            detected_at=datetime.now(timezone.utc),
            evidence_snapshot={
                "source": data.source,
                "source_url": str(data.source_url) if data.source_url else None,
                "import_type": "manual",
            },
            **data.model_dump(),
        )
        self.db.add(mention)
        self.db.commit()
        self.db.refresh(mention)
        return mention

    def update_mention(self, *, mention_id: UUID, data: MentionUpdate) -> Mention:
        mention = self.get_mention(mention_id)
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(mention, field, value)
        self.db.commit()
        self.db.refresh(mention)
        return mention

    def delete_mention(self, mention_id: UUID) -> None:
        mention = self.get_mention(mention_id)
        self.db.delete(mention)
        self.db.commit()

    def _ensure_clinic_exists(self, clinic_id: UUID) -> None:
        if self.db.get(Clinic, clinic_id) is None:
            raise ClinicNotFoundForMentionError
