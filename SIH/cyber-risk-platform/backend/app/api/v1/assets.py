import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.asset import AssetCreate, AssetRead, AssetUpdate
from app.services.asset_service import asset_service

router = APIRouter()

@router.post("/", response_model=AssetRead)
def create_asset(
    *,
    db: Session = Depends(get_db),
    asset_in: AssetCreate,
) -> Any:
    """
    Create new asset.
    """
    return asset_service.create(db, obj_in=asset_in)

@router.get("/", response_model=list[AssetRead])
def read_assets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve assets.
    """
    return asset_service.get_all(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=AssetRead)
def read_asset(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
) -> Any:
    """
    Get asset by ID.
    """
    asset = asset_service.get(db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.put("/{id}", response_model=AssetRead)
def update_asset(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
    asset_in: AssetUpdate,
) -> Any:
    """
    Update an asset.
    """
    asset = asset_service.get(db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset_service.update(db, db_obj=asset, obj_in=asset_in)

@router.delete("/{id}", response_model=AssetRead)
def delete_asset(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
) -> Any:
    """
    Delete an asset.
    """
    asset = asset_service.get(db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    asset_service.delete(db, db_obj=asset)
    return asset
