import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.control import SecurityControlCreate, SecurityControlRead
from app.services.control_service import control_service

router = APIRouter()

@router.post("/", response_model=SecurityControlRead)
def create_control(
    *,
    db: Session = Depends(get_db),
    control_in: SecurityControlCreate,
) -> Any:
    """
    Create new security control.
    """
    return control_service.create(db, obj_in=control_in)

@router.get("/", response_model=list[SecurityControlRead])
def read_controls(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve security controls.
    """
    return control_service.get_all(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=SecurityControlRead)
def read_control(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
) -> Any:
    """
    Get security control by ID.
    """
    control = control_service.get(db, id=id)
    if not control:
        raise HTTPException(status_code=404, detail="Security control not found")
    return control
