from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.clinic import Clinic
from app.db.models.keyword import Keyword, KeywordVersion
from app.modules.keywords.schemas import KeywordCreate, KeywordUpdate


class KeywordNotFoundError(Exception):
    pass


class KeywordConflictError(Exception):
    pass


class ClinicNotFoundForKeywordError(Exception):
    pass


class KeywordService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_keywords(
        self,
        *,
        clinic_id: UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Keyword]:
        self._ensure_clinic_exists(clinic_id)
        statement = (
            select(Keyword)
            .where(Keyword.clinic_id == clinic_id)
            .order_by(Keyword.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement))

    def get_keyword(self, keyword_id: UUID) -> Keyword:
        keyword = self.db.get(Keyword, keyword_id)
        if keyword is None:
            raise KeywordNotFoundError
        return keyword

    def create_keyword(
        self,
        *,
        clinic_id: UUID,
        data: KeywordCreate,
        created_by_id: UUID | None = None,
    ) -> Keyword:
        self._ensure_clinic_exists(clinic_id)
        self._ensure_unique_value(clinic_id=clinic_id, value=data.value)

        keyword = Keyword(
            clinic_id=clinic_id,
            created_by_id=created_by_id,
            **data.model_dump(),
        )
        self.db.add(keyword)
        self.db.flush()
        self.db.add(
            KeywordVersion(
                keyword_id=keyword.id,
                old_value=None,
                new_value=keyword.value,
                changed_by_id=created_by_id,
            )
        )
        self.db.commit()
        self.db.refresh(keyword)
        return keyword

    def update_keyword(
        self,
        *,
        keyword_id: UUID,
        data: KeywordUpdate,
        changed_by_id: UUID | None = None,
    ) -> Keyword:
        keyword = self.get_keyword(keyword_id)
        updates = data.model_dump(exclude_unset=True)

        if "value" in updates and updates["value"] != keyword.value:
            self._ensure_unique_value(
                clinic_id=keyword.clinic_id,
                value=updates["value"],
                exclude_keyword_id=keyword.id,
            )
            self.db.add(
                KeywordVersion(
                    keyword_id=keyword.id,
                    old_value=keyword.value,
                    new_value=updates["value"],
                    changed_by_id=changed_by_id,
                )
            )

        for field, value in updates.items():
            setattr(keyword, field, value)

        self.db.commit()
        self.db.refresh(keyword)
        return keyword

    def delete_keyword(self, keyword_id: UUID) -> None:
        keyword = self.get_keyword(keyword_id)
        self.db.delete(keyword)
        self.db.commit()

    def _ensure_clinic_exists(self, clinic_id: UUID) -> None:
        if self.db.get(Clinic, clinic_id) is None:
            raise ClinicNotFoundForKeywordError

    def _ensure_unique_value(
        self,
        *,
        clinic_id: UUID,
        value: str,
        exclude_keyword_id: UUID | None = None,
    ) -> None:
        statement = select(Keyword).where(
            Keyword.clinic_id == clinic_id,
            func.lower(Keyword.value) == value.lower(),
        )
        if exclude_keyword_id is not None:
            statement = statement.where(Keyword.id != exclude_keyword_id)

        if self.db.scalars(statement).first() is not None:
            raise KeywordConflictError
