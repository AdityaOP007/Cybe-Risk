import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.recommendation import Recommendation
from app.schemas.recommendation import RecommendationRead, RecommendationUpdate
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter()

@router.post("/generate", response_model=List[RecommendationRead])
def generate_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger the recommendation engine to scan assets and generate new prioritized mitigations.
    """
    engine = RecommendationEngine(db)
    recs = engine.generate_recommendations(current_user.organization_id)
    return recs

@router.get("/", response_model=List[RecommendationRead])
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all active prioritized recommendations for the organization.
    """
    engine = RecommendationEngine(db)
    recs = engine._get_active_recommendations(current_user.organization_id)
    return recs

@router.patch("/{recommendation_id}", response_model=RecommendationRead)
def update_recommendation(
    recommendation_id: uuid.UUID,
    update_data: RecommendationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a recommendation (e.g., mark as accepted or completed).
    """
    rec = db.scalar(select(Recommendation).where(Recommendation.id == recommendation_id, Recommendation.organization_id == current_user.organization_id))
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if update_data.status:
        rec.status = update_data.status
    if update_data.accepted_at:
        rec.accepted_at = update_data.accepted_at
    if update_data.completed_at:
        rec.completed_at = update_data.completed_at

    db.commit()
    db.refresh(rec)
    return rec
