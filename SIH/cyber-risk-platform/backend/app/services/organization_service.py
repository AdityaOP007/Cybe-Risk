import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate

class OrganizationService:
    @staticmethod
    def create(db: Session, obj_in: OrganizationCreate) -> Organization:
        db_obj = Organization(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get(db: Session, id: uuid.UUID) -> Organization | None:
        return db.get(Organization, id)

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Organization]:
        return db.scalars(select(Organization).offset(skip).limit(limit)).all()

    @staticmethod
    def update(db: Session, db_obj: Organization, obj_in: OrganizationUpdate) -> Organization:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, db_obj: Organization) -> None:
        db.delete(db_obj)
        db.commit()

organization_service = OrganizationService()
