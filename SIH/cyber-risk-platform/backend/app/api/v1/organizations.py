import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.organization import OrganizationCreate, OrganizationRead, OrganizationUpdate
from app.services.organization_service import organization_service

router = APIRouter()

@router.post("/", response_model=OrganizationRead)
def create_organization(
    *,
    db: Session = Depends(get_db),
    org_in: OrganizationCreate,
) -> Any:
    """
    Create new organization.
    """
    return organization_service.create(db, obj_in=org_in)

@router.get("/", response_model=list[OrganizationRead])
def read_organizations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve organizations.
    """
    return organization_service.get_all(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=OrganizationRead)
def read_organization(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
) -> Any:
    """
    Get organization by ID.
    """
    org = organization_service.get(db, id=id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
