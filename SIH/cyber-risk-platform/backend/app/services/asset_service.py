import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate

class AssetService:
    @staticmethod
    def create(db: Session, obj_in: AssetCreate) -> Asset:
        db_obj = Asset(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get(db: Session, id: uuid.UUID) -> Asset | None:
        return db.get(Asset, id)

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Asset]:
        return db.scalars(select(Asset).offset(skip).limit(limit)).all()

    @staticmethod
    def update(db: Session, db_obj: Asset, obj_in: AssetUpdate) -> Asset:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, db_obj: Asset) -> None:
        db.delete(db_obj)
        db.commit()

asset_service = AssetService()
