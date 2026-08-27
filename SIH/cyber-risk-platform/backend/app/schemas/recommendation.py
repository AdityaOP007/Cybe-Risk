import uuid
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Any, Optional, List

class RecommendationEvidence(BaseModel):
    source: str # e.g., "Threat Intelligence", "Vulnerability Scanner", "AI Prediction"
    detail: str # e.g., "CVE-2023-1234 actively exploited by APT29"
    severity: str # "Critical", "High", "Medium", "Low"

class RecommendationMetadata(BaseModel):
    rationale: str
    risk_driver: str
    urgency: str # "Immediate", "24 Hours", "7 Days", "30 Days"
    expected_financial_benefit: Optional[float] = None # EAL reduced
    implementation_effort: str # "Low", "Medium", "High"
    confidence: float # 0-100
    evidence: List[RecommendationEvidence] = Field(default_factory=list)

class RecommendationBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str # "Critical", "High", "Medium", "Low"
    estimated_cost: Optional[float] = None
    expected_risk_reduction: Optional[float] = None
    status: str = "proposed"

class RecommendationCreate(RecommendationBase):
    organization_id: uuid.UUID
    asset_id: Optional[uuid.UUID] = None
    metadata_: Optional[RecommendationMetadata] = Field(None, alias="metadata")

class RecommendationUpdate(BaseModel):
    status: Optional[str] = None
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class RecommendationRead(RecommendationBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    asset_id: Optional[uuid.UUID] = None
    generated_at: datetime
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata_: Optional[RecommendationMetadata] = Field(None, alias="metadata")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
