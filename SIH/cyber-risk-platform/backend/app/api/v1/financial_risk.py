from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid

from app.core.database import get_db
from app.schemas.financial_risk import (
    FinancialRiskAssessmentRead,
    FinancialBreakdown,
    FinancialAssumptionRead,
    OrganizationFinancialRiskSummary
)
from app.models.financial_risk import FinancialRiskAssessment, FinancialAssumption
from app.models.asset import Asset
from app.services.financial_risk import FinancialRiskEngine

router = APIRouter(prefix="/financial-risk", tags=["Financial Risk"])

# ---------------------------------------------------------------------------
# ASSET ENDPOINTS
# ---------------------------------------------------------------------------

@router.post("/assets/{asset_id}/calculate", response_model=FinancialRiskAssessmentRead)
def calculate_asset_financial_risk(asset_id: uuid.UUID, db: Session = Depends(get_db)):
    """Calculates and persists the financial risk for an asset based on latest cyber risk and assumptions."""
    engine = FinancialRiskEngine(db)
    try:
        return engine.calculate_asset_financial_risk(asset_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/assets/{asset_id}", response_model=FinancialRiskAssessmentRead)
def get_asset_financial_risk(asset_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retrieves the latest financial risk assessment for an asset."""
    assessment = db.query(FinancialRiskAssessment).filter(
        FinancialRiskAssessment.asset_id == asset_id
    ).order_by(desc(FinancialRiskAssessment.calculated_at)).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="No financial risk assessment found for this asset")
    return assessment

@router.get("/assets/{asset_id}/history", response_model=List[FinancialRiskAssessmentRead])
def get_asset_financial_risk_history(asset_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retrieves historical financial risk assessments for an asset."""
    return db.query(FinancialRiskAssessment).filter(
        FinancialRiskAssessment.asset_id == asset_id
    ).order_by(desc(FinancialRiskAssessment.calculated_at)).all()

@router.get("/assets/{asset_id}/breakdown", response_model=FinancialBreakdown)
def get_asset_financial_breakdown(asset_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retrieves the exact monetary breakdown of the latest financial risk assessment."""
    assessment = db.query(FinancialRiskAssessment).filter(
        FinancialRiskAssessment.asset_id == asset_id
    ).order_by(desc(FinancialRiskAssessment.calculated_at)).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="No financial risk assessment found")
        
    return FinancialBreakdown(
        direct_loss=assessment.direct_loss,
        data_loss=assessment.data_loss,
        business_interruption_loss=assessment.business_interruption_loss,
        recovery_loss=assessment.recovery_loss,
        customer_impact=assessment.customer_impact,
        third_party_impact=assessment.third_party_impact,
        regulatory_legal_exposure=assessment.regulatory_legal_exposure,
        fraud_loss=assessment.fraud_loss,
        reputation_revenue_impact=assessment.reputation_revenue_impact
    )

@router.get("/assets/{asset_id}/assumptions", response_model=List[FinancialAssumptionRead])
def get_asset_assumptions(asset_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retrieves the financial assumptions associated with the asset's organization."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    assumptions = db.query(FinancialAssumption).filter(
        FinancialAssumption.organization_id == asset.organization_id
    ).all()
    return assumptions


# ---------------------------------------------------------------------------
# ORGANIZATION ENDPOINTS
# ---------------------------------------------------------------------------

@router.post("/organizations/{organization_id}/calculate", response_model=dict)
def calculate_org_financial_risk(organization_id: uuid.UUID, db: Session = Depends(get_db)):
    """Triggers recalculation for all assets in the organization."""
    engine = FinancialRiskEngine(db)
    engine.calculate_organization_financial_risk(organization_id)
    return {"status": "success", "message": "Recalculated financial risk for organization assets"}

@router.get("/organizations/{organization_id}", response_model=OrganizationFinancialRiskSummary)
def get_org_financial_risk(organization_id: uuid.UUID, db: Session = Depends(get_db)):
    """Aggregates the latest financial risk across the organization."""
    
    assets = db.query(Asset).filter(Asset.organization_id == organization_id).all()
    
    total_potential_loss = 0.0
    total_eal = 0.0
    total_confidence = 0.0
    
    b_direct = 0.0
    b_data = 0.0
    b_bi = 0.0
    b_recovery = 0.0
    b_customer = 0.0
    b_third = 0.0
    b_reg = 0.0
    b_fraud = 0.0
    b_rep = 0.0
    
    asset_assessments = []
    
    for asset in assets:
        latest = db.query(FinancialRiskAssessment).filter(
            FinancialRiskAssessment.asset_id == asset.id
        ).order_by(desc(FinancialRiskAssessment.calculated_at)).first()
        
        if latest:
            asset_assessments.append(latest)
            total_potential_loss += float(latest.potential_loss)
            total_eal += float(latest.expected_loss)
            total_confidence += float(latest.confidence)
            
            b_direct += float(latest.direct_loss)
            b_data += float(latest.data_loss)
            b_bi += float(latest.business_interruption_loss)
            b_recovery += float(latest.recovery_loss)
            b_customer += float(latest.customer_impact)
            b_third += float(latest.third_party_impact)
            b_reg += float(latest.regulatory_legal_exposure)
            b_fraud += float(latest.fraud_loss)
            b_rep += float(latest.reputation_revenue_impact)
            
    if not asset_assessments:
        raise HTTPException(status_code=404, detail="No financial risk data for organization")
        
    avg_confidence = total_confidence / len(asset_assessments)
    
    # Sort top financial risk assets by EAL
    top_assets = sorted(asset_assessments, key=lambda x: x.expected_loss, reverse=True)[:5]
    
    breakdown = FinancialBreakdown(
        direct_loss=b_direct,
        data_loss=b_data,
        business_interruption_loss=b_bi,
        recovery_loss=b_recovery,
        customer_impact=b_customer,
        third_party_impact=b_third,
        regulatory_legal_exposure=b_reg,
        fraud_loss=b_fraud,
        reputation_revenue_impact=b_rep
    )
    
    return OrganizationFinancialRiskSummary(
        organization_id=organization_id,
        total_potential_loss=total_potential_loss,
        total_expected_annual_loss=total_eal,
        top_financial_risk_assets=top_assets,
        aggregate_breakdown=breakdown,
        average_confidence=avg_confidence
    )
