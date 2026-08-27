import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from math import ceil

from app.core.database import get_db
from app.schemas.asset import (
    AssetCreate, 
    AssetRead, 
    AssetUpdate, 
    PaginatedAssetsResponse, 
    AssetPostureResponse
)
from app.schemas.vulnerability import VulnerabilityRead
from app.schemas.telemetry import TelemetryEventRead
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

@router.get("/", response_model=PaginatedAssetsResponse)
def read_assets(
    db: Session = Depends(get_db),
    organization_id: uuid.UUID | None = Query(None, description="Filter by Organization ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search term for names, hostnames, owners"),
    asset_type: str | None = None,
    environment: str | None = None,
    status: str | None = None,
    internet_exposed: bool | None = None,
    criticality_min: int | None = Query(None, ge=0, le=100),
    criticality_max: int | None = Query(None, ge=0, le=100),
    department: str | None = None,
    owner: str | None = None,
    sort_by: str = Query("created_at", description="Field to sort by (e.g. name, criticality)"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
) -> Any:
    """
    Retrieve assets with pagination, filtering, and search.
    """
    skip = (page - 1) * page_size
    items, total = asset_service.get_all(
        db,
        organization_id=organization_id,
        skip=skip,
        limit=page_size,
        search=search,
        asset_type=asset_type,
        environment=environment,
        status=status,
        internet_exposed=internet_exposed,
        criticality_min=criticality_min,
        criticality_max=criticality_max,
        department=department,
        owner=owner,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    total_pages = ceil(total / page_size) if total > 0 else 1
    
    return PaginatedAssetsResponse(
        items=list(items),
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages
    )

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

@router.post("/{id}/retire", response_model=dict)
def retire_asset(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
) -> Any:
    """
    Retire an asset safely without deleting historical records.
    """
    asset = asset_service.get(db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset_service.retire(db, db_obj=asset)
    return {"message": "Asset retired successfully", "asset_id": str(id)}

@router.get("/{id}/posture", response_model=AssetPostureResponse)
def read_asset_posture(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
) -> Any:
    """
    Get basic security posture aggregation for the asset.
    """
    return asset_service.get_posture(db, asset_id=id)

@router.get("/{id}/vulnerabilities", response_model=list[VulnerabilityRead])
def read_asset_vulnerabilities(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    severity: str | None = None,
    status: str | None = None,
) -> Any:
    """
    Get vulnerabilities for the asset.
    """
    asset = asset_service.get(db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    skip = (page - 1) * page_size
    return asset_service.get_vulnerabilities(
        db, asset_id=id, skip=skip, limit=page_size, severity=severity, status=status
    )

@router.get("/{id}/telemetry", response_model=list[TelemetryEventRead])
def read_asset_telemetry(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    severity: str | None = None,
    event_type: str | None = None,
) -> Any:
    """
    Get telemetry events for the asset.
    """
    asset = asset_service.get(db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    skip = (page - 1) * page_size
    return asset_service.get_telemetry(
        db, asset_id=id, skip=skip, limit=page_size, severity=severity, event_type=event_type
    )

@router.get("/{id}/threat-intelligence", response_model=list[Any])
def read_asset_threat_intelligence(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
) -> Any:
    """
    Get threat intelligence correlated with this asset.
    """
    from app.models.threat_intel import ThreatCorrelation
    
    asset = asset_service.get(db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    correlations = db.query(ThreatCorrelation).filter(
        ThreatCorrelation.asset_id == id
    ).all()
    
    return correlations

@router.delete("/{id}", response_model=AssetRead)
def delete_asset(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
) -> Any:
    """
    Physical deletion of an asset.
    """
    asset = asset_service.get(db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    asset_service.delete(db, db_obj=asset)
    return asset
