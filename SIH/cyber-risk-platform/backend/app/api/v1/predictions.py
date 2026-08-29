import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.prediction import RiskPrediction, RiskPredictionModel
from app.schemas.prediction import (
    RiskPredictionRead, 
    AssetRiskForecastResponse,
    OrganizationRiskForecastResponse,
    PredictionBulkResult,
    RiskPredictionModelRead
)
from app.services.prediction.engine import PredictionEngine
from app.models.asset import Asset
from app.models.organization import Organization

router = APIRouter()

@router.post("/assets/{asset_id}/calculate", response_model=AssetRiskForecastResponse)
def calculate_asset_prediction(
    asset_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate predictions for 7, 30, and 90 days for a specific asset.
    """
    asset = db.scalar(select(Asset).where(Asset.id == asset_id))
    if not asset or asset.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Asset not found")

    engine = PredictionEngine(db)
    
    forecasts = {}
    last_metadata = {}
    
    for horizon in [7, 30, 90]:
        try:
            pred = engine.generate_prediction(
                asset_id=asset_id,
                organization_id=current_user.organization_id,
                horizon_days=horizon
            )
            forecasts[horizon] = pred
            last_metadata = pred.prediction_metadata
        except ValueError as e:
            # Propagate up e.g., "Insufficient historical data"
            raise HTTPException(status_code=422, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail="Prediction model error")
            
    # Assemble response
    from app.models.risk import RiskScore
    from app.models.financial_risk import FinancialRiskAssessment
    
    current_risk = db.scalar(
        select(RiskScore).where(RiskScore.asset_id == asset_id).order_by(desc(RiskScore.calculated_at)).limit(1)
    )
    fin_risk = db.scalar(
        select(FinancialRiskAssessment).where(FinancialRiskAssessment.asset_id == asset_id).order_by(desc(FinancialRiskAssessment.calculated_at)).limit(1)
    )

    drivers = last_metadata.get("drivers", []) if last_metadata else []
    
    return AssetRiskForecastResponse(
        asset_id=asset_id,
        current_risk=current_risk.score if current_risk else 0,
        current_financial_exposure=fin_risk.expected_loss if fin_risk else None,
        forecasts=forecasts,
        drivers=drivers
    )


@router.get("/assets/{asset_id}", response_model=AssetRiskForecastResponse)
def get_asset_prediction(
    asset_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve latest stored predictions for an asset.
    """
    asset = db.scalar(select(Asset).where(Asset.id == asset_id))
    if not asset or asset.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Asset not found")

    forecasts = {}
    last_metadata = {}
    
    for horizon in [7, 30, 90]:
        pred = db.scalar(
            select(RiskPrediction)
            .where(RiskPrediction.asset_id == asset_id)
            .where(RiskPrediction.forecast_horizon_days == horizon)
            .order_by(desc(RiskPrediction.prediction_timestamp))
            .limit(1)
        )
        if pred:
            forecasts[horizon] = pred
            last_metadata = pred.prediction_metadata

    if not forecasts:
        raise HTTPException(status_code=404, detail="No predictions found for asset")
        
    from app.models.risk import RiskScore
    from app.models.financial_risk import FinancialRiskAssessment
    
    current_risk = db.scalar(
        select(RiskScore).where(RiskScore.asset_id == asset_id).order_by(desc(RiskScore.calculated_at)).limit(1)
    )
    fin_risk = db.scalar(
        select(FinancialRiskAssessment).where(FinancialRiskAssessment.asset_id == asset_id).order_by(desc(FinancialRiskAssessment.calculated_at)).limit(1)
    )

    drivers = last_metadata.get("drivers", []) if last_metadata else []

    return AssetRiskForecastResponse(
        asset_id=asset_id,
        current_risk=current_risk.score if current_risk else 0,
        current_financial_exposure=fin_risk.expected_loss if fin_risk else None,
        forecasts=forecasts,
        drivers=drivers
    )

@router.post("/organizations/{organization_id}/calculate-all", response_model=PredictionBulkResult)
def calculate_all_predictions(
    organization_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate predictions for all assets in the organization.
    """
    if organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized for this organization")
        
    assets = db.scalars(select(Asset).where(Asset.organization_id == organization_id)).all()
    
    engine = PredictionEngine(db)
    
    result = PredictionBulkResult(
        assets_processed=len(assets),
        predictions_generated=0,
        insufficient_data=0,
        failed=0
    )
    
    for asset in assets:
        try:
            for h in [7, 30, 90]:
                engine.generate_prediction(asset.id, organization_id, h)
            result.predictions_generated += 1
        except ValueError:
            result.insufficient_data += 1
        except Exception:
            result.failed += 1
            
    return result

@router.get("/models", response_model=List[RiskPredictionModelRead])
def get_prediction_models(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get all registered ML models.
    """
    models = db.scalars(select(RiskPredictionModel).order_by(desc(RiskPredictionModel.created_at))).all()
    return models
