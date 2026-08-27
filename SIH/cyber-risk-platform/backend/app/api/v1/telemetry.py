import uuid
import csv
import io
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from math import ceil

from app.core.database import get_db
from app.schemas.telemetry import (
    TelemetryEventCreate, 
    TelemetryEventRead, 
    TelemetryEventBatch, 
    TelemetryBatchResult, 
    PaginatedTelemetry, 
    TelemetryStats
)
from app.services.telemetry_service import telemetry_service

router = APIRouter()

@router.post("/events", response_model=TelemetryEventRead, status_code=201)
def create_telemetry_event(
    *,
    db: Session = Depends(get_db),
    event_in: TelemetryEventCreate,
) -> Any:
    """
    Ingest a single telemetry event.
    """
    try:
        return telemetry_service.create(db, obj_in=event_in)
    except ValueError as e:
        if "Duplicate" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/events/batch", response_model=TelemetryBatchResult)
def create_telemetry_batch(
    *,
    db: Session = Depends(get_db),
    batch_in: TelemetryEventBatch,
) -> Any:
    """
    Ingest a batch of telemetry events.
    """
    return telemetry_service.create_batch(db, events_in=batch_in.events)

@router.post("/events/upload", response_model=TelemetryBatchResult)
async def upload_telemetry_csv(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
) -> Any:
    """
    Ingest telemetry events from a CSV file.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    content = await file.read()
    text_content = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text_content))
    
    events = []
    for row in reader:
        try:
            # Basic parsing of CSV strings to proper types
            org_id = uuid.UUID(row.get('organization_id', '').strip())
            
            asset_id_str = row.get('asset_id', '').strip()
            asset_id = uuid.UUID(asset_id_str) if asset_id_str else None
            
            occurred_at_str = row.get('occurred_at', '').strip()
            occurred_at = datetime.fromisoformat(occurred_at_str.replace('Z', '+00:00')) if occurred_at_str else None
            
            import json
            event_data_str = row.get('event_data', '').strip()
            event_data = json.loads(event_data_str) if event_data_str else {}
            
            event = TelemetryEventCreate(
                organization_id=org_id,
                asset_id=asset_id,
                source=row.get('source', '').strip(),
                event_type=row.get('event_type', '').strip(),
                severity=row.get('severity', '').strip(),
                message=row.get('message', '').strip() or None,
                source_event_id=row.get('source_event_id', '').strip() or None,
                occurred_at=occurred_at,
                event_data=event_data
            )
            events.append(event)
        except Exception as e:
            # Fast fail if CSV is fundamentally broken
            raise HTTPException(status_code=400, detail=f"Invalid CSV row format: {str(e)}")

    return telemetry_service.create_batch(db, events_in=events)

@router.get("/events", response_model=PaginatedTelemetry)
def read_telemetry_events(
    db: Session = Depends(get_db),
    organization_id: uuid.UUID | None = Query(None, description="Filter by Organization ID"),
    asset_id: uuid.UUID | None = Query(None, description="Filter by Asset ID"),
    source: str | None = None,
    event_type: str | None = None,
    severity: str | None = None,
    search: str | None = Query(None, description="Search term"),
    from_time: datetime | None = None,
    to_time: datetime | None = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    sort_by: str = Query("occurred_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
) -> Any:
    """
    Retrieve telemetry events with filtering and pagination.
    """
    skip = (page - 1) * page_size
    items, total = telemetry_service.get_all(
        db,
        organization_id=organization_id,
        asset_id=asset_id,
        source=source,
        event_type=event_type,
        severity=severity,
        search=search,
        from_time=from_time,
        to_time=to_time,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    total_pages = ceil(total / page_size) if total > 0 else 1
    
    return PaginatedTelemetry(
        items=list(items),
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages
    )

@router.get("/events/recent", response_model=list[TelemetryEventRead])
def read_recent_telemetry_events(
    db: Session = Depends(get_db),
    organization_id: uuid.UUID | None = Query(None),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """
    Get most recent telemetry events.
    """
    items, _ = telemetry_service.get_all(
        db,
        organization_id=organization_id,
        skip=0,
        limit=limit,
        sort_by="occurred_at",
        sort_order="desc"
    )
    return items

@router.get("/stats", response_model=TelemetryStats)
def read_telemetry_stats(
    db: Session = Depends(get_db),
    organization_id: uuid.UUID | None = Query(None)
) -> Any:
    """
    Get telemetry statistics.
    """
    return telemetry_service.get_stats(db, organization_id=organization_id)

@router.get("/events/{event_id}", response_model=TelemetryEventRead)
def read_telemetry_event(
    *,
    db: Session = Depends(get_db),
    event_id: uuid.UUID,
) -> Any:
    """
    Get a specific telemetry event by ID.
    """
    event = telemetry_service.get(db, id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Telemetry event not found")
    return event
