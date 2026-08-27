import uuid
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class RiskSummary(BaseModel):
    current_score: float
    risk_level: str
    previous_score: Optional[float] = None
    change: Optional[float] = None
    trend: str # increasing, stable, decreasing
    last_updated: datetime

class FinancialSummary(BaseModel):
    modeled_exposure: float
    expected_annual_loss: float
    breakdown: dict
    last_updated: datetime

class PredictionSummary(BaseModel):
    forecast_30_day: float
    trend: str
    confidence: float
    last_updated: datetime

class AssetRiskSummary(BaseModel):
    asset_id: uuid.UUID
    asset_name: str
    risk_score: float
    criticality: int
    financial_exposure: float
    predicted_risk: Optional[float] = None
    trend: str

class TopRiskDrivers(BaseModel):
    driver_name: str
    risk_contribution: float
    category: str

class ThreatSummary(BaseModel):
    threat_id: uuid.UUID
    name: str
    affected_assets: int
    confidence: float
    severity: str
    trend: str

class VulnerabilitySummary(BaseModel):
    vulnerability_id: uuid.UUID
    name: str
    severity: str
    known_exploited: bool
    affected_assets: int
    risk_contribution: float

class RecommendationSummary(BaseModel):
    recommendation_id: uuid.UUID
    action: str
    asset_name: Optional[str] = None
    priority: str
    estimated_risk_reduction: float
    financial_exposure_reduction: float
    urgency: str
    status: str

class BudgetSummary(BaseModel):
    recommended_budget: float
    budget_used: float
    budget_remaining: float
    selected_investments: int
    risk_before: float
    risk_after: float
    financial_exposure_before: float
    financial_exposure_after: float
    last_updated: datetime

class ComplianceSummary(BaseModel):
    framework_name: str
    coverage_percentage: float
    compliant: int
    partially_compliant: int
    non_compliant: int
    insufficient_evidence: int
    open_gaps: int

class DashboardAlertRead(BaseModel):
    id: uuid.UUID
    title: str
    reason: str
    source_module: str
    severity: str
    action_link: Optional[str] = None
    status: str
    first_seen: datetime
    last_seen: datetime

class ExecutiveInsightRead(BaseModel):
    id: uuid.UUID
    content: str
    insight_type: str
    generated_at: datetime

class DataQuality(BaseModel):
    risk_engine: str
    prediction: str
    financial_model: str
    compliance: str

class ExecutiveDashboardData(BaseModel):
    organization_id: uuid.UUID
    last_updated: datetime
    risk: RiskSummary
    financial: Optional[FinancialSummary] = None
    prediction: Optional[PredictionSummary] = None
    top_assets: List[AssetRiskSummary]
    risk_drivers: List[TopRiskDrivers]
    threats: List[ThreatSummary]
    vulnerabilities: List[VulnerabilitySummary]
    recommendations: List[RecommendationSummary]
    budget: Optional[BudgetSummary] = None
    compliance: List[ComplianceSummary]
    alerts: List[DashboardAlertRead]
    insights: List[ExecutiveInsightRead]
    data_quality: DataQuality
