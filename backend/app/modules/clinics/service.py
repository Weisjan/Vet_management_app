from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.clinic import Clinic
from app.modules.clinics.schemas import ClinicCreate, ClinicUpdate


class ClinicNotFoundError(Exception):
    pass


class ClinicService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_clinics(self, *, offset: int = 0, limit: int = 100) -> list[Clinic]:
        statement = select(Clinic).order_by(Clinic.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(statement))

    def get_clinic(self, clinic_id: UUID) -> Clinic:
        clinic = self.db.get(Clinic, clinic_id)
        if clinic is None:
            raise ClinicNotFoundError
        return clinic

    def create_clinic(self, data: ClinicCreate) -> Clinic:
        clinic = Clinic(**data.model_dump())
        self.db.add(clinic)
        self.db.commit()
        self.db.refresh(clinic)
        return clinic

    def update_clinic(self, clinic_id: UUID, data: ClinicUpdate) -> Clinic:
        clinic = self.get_clinic(clinic_id)
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(clinic, field, value)
        self.db.commit()
        self.db.refresh(clinic)
        return clinic

    def delete_clinic(self, clinic_id: UUID) -> None:
        clinic = self.get_clinic(clinic_id)
        self.db.delete(clinic)
        self.db.commit()
