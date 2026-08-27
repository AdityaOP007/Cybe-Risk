import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.control import SecurityControl
from app.schemas.control import SecurityControlCreate

class SecurityControlService:
    @staticmethod
    def create(db: Session, obj_in: SecurityControlCreate) -> SecurityControl:
        db_obj = SecurityControl(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get(db: Session, id: uuid.UUID) -> SecurityControl | None:
        return db.get(SecurityControl, id)

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[SecurityControl]:
        return db.scalars(select(SecurityControl).offset(skip).limit(limit)).all()

control_service = SecurityControlService()
