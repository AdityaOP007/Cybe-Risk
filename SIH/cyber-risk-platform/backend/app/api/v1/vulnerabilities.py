import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.vulnerability import VulnerabilityCreate, VulnerabilityRead
from app.services.vulnerability_service import vulnerability_service

router = APIRouter()

@router.post("/", response_model=VulnerabilityRead)
def create_vulnerability(
    *,
    db: Session = Depends(get_db),
    vulnerability_in: VulnerabilityCreate,
) -> Any:
    """
    Create new vulnerability.
    """
    return vulnerability_service.create(db, obj_in=vulnerability_in)

@router.get("/", response_model=list[VulnerabilityRead])
def read_vulnerabilities(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve vulnerabilities.
    """
    return vulnerability_service.get_all(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=VulnerabilityRead)
def read_vulnerability(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
) -> Any:
    """
    Get vulnerability by ID.
    """
    vulnerability = vulnerability_service.get(db, id=id)
    if not vulnerability:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vulnerability
