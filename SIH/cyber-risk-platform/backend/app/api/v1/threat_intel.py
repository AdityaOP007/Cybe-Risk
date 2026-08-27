import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.threat_intel import ThreatIntelligenceRecord, ThreatIndicator, ThreatCorrelation
from app.schemas.threat_intel import (
    ThreatIntelligenceRecordResponse, ThreatIntelligenceRecordCreate, 
    PaginatedThreatIntelligence, ThreatIntelligenceStats
)
from app.services.threat_intel_service import ThreatIntelligenceService
from app.services.correlation_engine import CorrelationEngine

router = APIRouter(prefix="/threat-intelligence", tags=["threat-intelligence"])


@router.post("/", response_model=ThreatIntelligenceRecordResponse, status_code=201)
def create_threat_intelligence(
    threat_in: ThreatIntelligenceRecordCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Ingest a new threat intelligence record.
    """
    service = ThreatIntelligenceService(db)
    record = service.ingest_record(threat_in)
    
    # Run correlation immediately for the prototype
    engine = CorrelationEngine(db)
    engine.run_full_correlation()
    
    return record


@router.get("/", response_model=PaginatedThreatIntelligence)
def get_threats(
    search: str | None = None,
    severity: str | None = None,
    source: str | None = None,
    intelligence_type: str | None = None,
    known_exploited: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    List threat intelligence records with filtering.
    """
    query = db.query(ThreatIntelligenceRecord)
    
    if search:
        query = query.filter(ThreatIntelligenceRecord.title.ilike(f"%{search}%"))
    if severity:
        query = query.filter(ThreatIntelligenceRecord.severity == severity.lower())
    if source:
        query = query.filter(ThreatIntelligenceRecord.source == source.lower())
    if intelligence_type:
        query = query.filter(ThreatIntelligenceRecord.intelligence_type == intelligence_type.lower())
    if known_exploited is not None:
        query = query.filter(ThreatIntelligenceRecord.known_exploited == known_exploited)
        
    total = query.count()
    items = query.order_by(ThreatIntelligenceRecord.last_seen_at.desc().nulls_last()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/stats", response_model=ThreatIntelligenceStats)
def get_threat_stats(db: Session = Depends(get_db)) -> Any:
    """
    Get aggregated statistics for threat intelligence.
    """
    total_threats = db.query(ThreatIntelligenceRecord).count()
    known_exploited = db.query(ThreatIntelligenceRecord).filter(ThreatIntelligenceRecord.known_exploited == True).count()
    
    critical = db.query(ThreatIntelligenceRecord).filter(ThreatIntelligenceRecord.severity == "critical").count()
    high = db.query(ThreatIntelligenceRecord).filter(ThreatIntelligenceRecord.severity == "high").count()
    medium = db.query(ThreatIntelligenceRecord).filter(ThreatIntelligenceRecord.severity == "medium").count()
    low = db.query(ThreatIntelligenceRecord).filter(ThreatIntelligenceRecord.severity == "low").count()
    informational = db.query(ThreatIntelligenceRecord).filter(ThreatIntelligenceRecord.severity == "informational").count()
    
    indicators = db.query(ThreatIndicator).count()
    
    # By source
    sources = db.query(ThreatIntelligenceRecord.source, func.count(ThreatIntelligenceRecord.id)).group_by(ThreatIntelligenceRecord.source).all()
    by_source = {s[0]: s[1] for s in sources}
    
    # By type
    types = db.query(ThreatIntelligenceRecord.intelligence_type, func.count(ThreatIntelligenceRecord.id)).group_by(ThreatIntelligenceRecord.intelligence_type).all()
    by_intelligence_type = {t[0]: t[1] for t in types}
    
    return {
        "total_threats": total_threats,
        "known_exploited": known_exploited,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "informational": informational,
        "indicators": indicators,
        "by_source": by_source,
        "by_intelligence_type": by_intelligence_type
    }


@router.get("/{threat_id}", response_model=ThreatIntelligenceRecordResponse)
def get_threat(threat_id: uuid.UUID, db: Session = Depends(get_db)) -> Any:
    """
    Get a specific threat intelligence record.
    """
    threat = db.query(ThreatIntelligenceRecord).filter(ThreatIntelligenceRecord.id == threat_id).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat intelligence record not found")
    return threat
