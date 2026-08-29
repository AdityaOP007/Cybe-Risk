from datetime import datetime
from uuid import UUID
from typing import Any, Optional
from pydantic import BaseModel, Field

class RiskFactors(BaseModel):
    impact: Optional[float] = None
    likelihood: Optional[float] = None
    gross_risk: Optional[float] = None
    mitigation_factor: Optional[float] = None
    total_assets: Optional[int] = None
    critical_assets: Optional[int] = None

class RiskMetadata(BaseModel):
    factors: RiskFactors = Field(default_factory=RiskFactors)
    drivers: list[str] = Field(default_factory=list)
    explanation: str = ""
    confidence: int = Field(0, ge=0, le=100)

class RiskScoreBase(BaseModel):
    score: float = Field(..., ge=0, le=100)
    risk_level: str
    calculation_version: Optional[str] = None
    risk_metadata: Optional[RiskMetadata] = None

class RiskScoreCreate(RiskScoreBase):
    organization_id: UUID
    asset_id: Optional[UUID] = None

class RiskScoreRead(RiskScoreBase):
    id: UUID
    organization_id: UUID
    asset_id: Optional[UUID] = None
    calculated_at: datetime
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class RiskTrendDataPoint(BaseModel):
    timestamp: datetime
    score: float
    risk_level: str

class RiskTrendResponse(BaseModel):
    current_score: RiskScoreRead
    historical_trend: list[RiskTrendDataPoint]
