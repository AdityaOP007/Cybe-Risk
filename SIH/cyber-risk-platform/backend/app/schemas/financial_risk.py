from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Financial Assumption Schemas
# ---------------------------------------------------------------------------
class FinancialAssumptionBase(BaseModel):
    category: str = Field(..., max_length=100)
    name: str = Field(..., max_length=255)
    value: float
    unit: Optional[str] = Field(None, max_length=50)
    currency: Optional[str] = Field("INR", max_length=10)
    source: str = Field(..., max_length=255)
    confidence: float = Field(..., ge=0.0, le=100.0)

class FinancialAssumptionCreate(FinancialAssumptionBase):
    organization_id: UUID

class FinancialAssumptionUpdate(BaseModel):
    value: Optional[float] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=100.0)
    source: Optional[str] = Field(None, max_length=255)

class FinancialAssumptionRead(FinancialAssumptionBase):
    id: UUID
    organization_id: UUID
    effective_from: datetime
    effective_until: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Financial Risk Breakdown
# ---------------------------------------------------------------------------
class FinancialBreakdown(BaseModel):
    direct_loss: float
    data_loss: float
    business_interruption_loss: float
    recovery_loss: float
    customer_impact: float
    third_party_impact: float
    regulatory_legal_exposure: float
    fraud_loss: float
    reputation_revenue_impact: float


# ---------------------------------------------------------------------------
# Financial Risk Assessment Schemas
# ---------------------------------------------------------------------------
class FinancialRiskAssessmentBase(BaseModel):
    potential_loss: float = Field(..., ge=0.0)
    expected_loss: float = Field(..., ge=0.0)
    annualized_expected_loss: float = Field(..., ge=0.0)
    
    direct_loss: float = 0.0
    data_loss: float = 0.0
    business_interruption_loss: float = 0.0
    recovery_loss: float = 0.0
    customer_impact: float = 0.0
    third_party_impact: float = 0.0
    regulatory_legal_exposure: float = 0.0
    fraud_loss: float = 0.0
    reputation_revenue_impact: float = 0.0
    
    confidence: float = Field(..., ge=0.0, le=100.0)
    data_completeness: float = Field(..., ge=0.0, le=100.0)
    
    currency: str = "INR"
    calculation_version: str
    
    assumptions_snapshot: Optional[Dict[str, Any]] = None
    financial_metadata: Optional[Dict[str, Any]] = None

class FinancialRiskAssessmentRead(FinancialRiskAssessmentBase):
    id: UUID
    organization_id: UUID
    asset_id: UUID
    risk_score_id: UUID
    calculated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}

class OrganizationFinancialRiskSummary(BaseModel):
    organization_id: UUID
    currency: str = "INR"
    total_potential_loss: float
    total_expected_annual_loss: float
    top_financial_risk_assets: List[FinancialRiskAssessmentRead]
    aggregate_breakdown: FinancialBreakdown
    average_confidence: float
