import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.risk import RiskScore
from app.models.asset import Asset
from app.models.organization import Organization
from app.schemas.risk import RiskScoreRead, RiskTrendResponse, RiskTrendDataPoint
from app.services.risk_engine import RiskEngine

router = APIRouter(prefix="/risk", tags=["Risk Quantification"])


@router.post("/calculate/asset/{asset_id}", response_model=RiskScoreRead)
def calculate_asset_risk(
    asset_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> Any:
    """
    Triggers the risk calculation engine for a specific asset.
    """
    engine = RiskEngine(db)
    try:
        score = engine.calculate_asset_risk(asset_id)
        return score
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/calculate/organization/{org_id}", response_model=RiskScoreRead)
def calculate_organization_risk(
    org_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> Any:
    """
    Triggers the risk calculation engine for an entire organization.
    """
    # Check if org exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    engine = RiskEngine(db)
    score = engine.calculate_organization_risk(org_id)
    return score


@router.get("/assets/{asset_id}", response_model=RiskTrendResponse)
def get_asset_risk(
    asset_id: uuid.UUID,
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get current risk score and historical trend for an asset.
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    scores = db.query(RiskScore).filter(
        RiskScore.asset_id == asset_id
    ).order_by(RiskScore.calculated_at.desc()).limit(limit).all()

    if not scores:
        # Calculate it if it doesn't exist
        engine = RiskEngine(db)
        current = engine.calculate_asset_risk(asset_id)
        scores = [current]
        
    current_score = scores[0]
    
    trend = [
        RiskTrendDataPoint(
            timestamp=s.calculated_at,
            score=s.score,
            risk_level=s.risk_level
        ) for s in reversed(scores)
    ]
    
    return {
        "current_score": current_score,
        "historical_trend": trend
    }


@router.get("/organizations/{org_id}", response_model=RiskTrendResponse)
def get_organization_risk(
    org_id: uuid.UUID,
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get current risk score and historical trend for an organization.
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Only get org-level scores (asset_id IS NULL)
    scores = db.query(RiskScore).filter(
        RiskScore.organization_id == org_id,
        RiskScore.asset_id == None
    ).order_by(RiskScore.calculated_at.desc()).limit(limit).all()

    if not scores:
        engine = RiskEngine(db)
        current = engine.calculate_organization_risk(org_id)
        scores = [current]
        
    current_score = scores[0]
    
    trend = [
        RiskTrendDataPoint(
            timestamp=s.calculated_at,
            score=s.score,
            risk_level=s.risk_level
        ) for s in reversed(scores)
    ]
    
    return {
        "current_score": current_score,
        "historical_trend": trend
    }
