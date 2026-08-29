import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Optional, List

# ---------------------------------------------------------
# Cybersecurity Investment Candidates
# ---------------------------------------------------------
class CybersecurityInvestmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    cost: float = 0.0
    currency: str = "INR"
    cost_type: str = "one_time"
    annualized_cost: Optional[float] = None
    implementation_effort: Optional[str] = None
    risk_reduction: Optional[float] = None
    financial_reduction: Optional[float] = None
    confidence: Optional[float] = None
    priority: Optional[str] = None
    urgency: Optional[str] = None
    dependencies: Optional[List[str]] = None
    conflicts: Optional[List[str]] = None
    mandatory: bool = False
    status: str = "candidate"

class CybersecurityInvestmentCreate(CybersecurityInvestmentBase):
    organization_id: uuid.UUID
    recommendation_id: Optional[uuid.UUID] = None
    asset_id: Optional[uuid.UUID] = None

class CybersecurityInvestmentRead(CybersecurityInvestmentBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    recommendation_id: Optional[uuid.UUID] = None
    asset_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------
# Optimization Configuration & Output
# ---------------------------------------------------------
class OptimizationWeights(BaseModel):
    risk_weight: float = 0.4
    financial_weight: float = 0.3
    criticality_weight: float = 0.15
    urgency_weight: float = 0.10
    confidence_weight: float = 0.05

class OptimizationRunRequest(BaseModel):
    budget: float
    currency: str = "INR"
    horizon_months: int = 12
    objective: str = "balanced" # risk_first, financial_first, balanced, minimum_residual_risk
    weights: OptimizationWeights = Field(default_factory=OptimizationWeights)

class OptimizationPortfolioRead(BaseModel):
    id: uuid.UUID
    optimization_run_id: uuid.UUID
    organization_id: uuid.UUID
    selected_investments: List[str]
    total_cost: float
    risk_reduction: Optional[float] = None
    financial_reduction: Optional[float] = None
    portfolio_metadata: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class OptimizationRunRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    budget: float
    currency: str
    horizon_months: int
    objective: str
    risk_weight: float
    financial_weight: float
    criticality_weight: float
    urgency_weight: float
    confidence_weight: float
    optimization_status: str
    total_cost: float
    remaining_budget: float
    risk_before: Optional[float] = None
    risk_after: Optional[float] = None
    risk_reduction: Optional[float] = None
    financial_before: Optional[float] = None
    financial_after: Optional[float] = None
    financial_reduction: Optional[float] = None
    optimization_score: Optional[float] = None
    calculation_version: str
    portfolios: List[OptimizationPortfolioRead] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------
# Scenario Simulation
# ---------------------------------------------------------
class RiskScenarioBase(BaseModel):
    name: str
    description: Optional[str] = None
    investments_applied: List[str]

class RiskScenarioCreate(RiskScenarioBase):
    pass

class RiskScenarioRead(RiskScenarioBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    optimization_portfolio_id: Optional[uuid.UUID] = None
    risk_before: Optional[float] = None
    risk_after: Optional[float] = None
    financial_before: Optional[float] = None
    financial_after: Optional[float] = None
    scenario_version: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
