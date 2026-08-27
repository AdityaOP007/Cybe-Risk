from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime

class PredictionDriver(BaseModel):
    feature: str
    importance: float
    direction: str # "increasing" or "decreasing"
    description: str

class RiskPredictionModelBase(BaseModel):
    name: str
    version: str
    model_type: str
    dataset_version: str
    feature_version: str
    status: str

class RiskPredictionModelRead(RiskPredictionModelBase):
    id: uuid.UUID
    metrics: Optional[Dict[str, Any]] = None
    training_started_at: datetime
    training_completed_at: datetime
    training_data_start: Optional[datetime] = None
    training_data_end: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RiskPredictionBase(BaseModel):
    forecast_horizon_days: int
    predicted_risk: float
    lower_bound: float
    upper_bound: float
    trend: str
    confidence: float
    
    predicted_financial_exposure: Optional[float] = None
    financial_lower_bound: Optional[float] = None
    financial_upper_bound: Optional[float] = None

class RiskPredictionCreate(RiskPredictionBase):
    organization_id: uuid.UUID
    asset_id: uuid.UUID
    risk_score_id: uuid.UUID
    model_name: str
    model_version: str
    feature_version: str
    dataset_version: str
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")

class RiskPredictionRead(RiskPredictionBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    asset_id: uuid.UUID
    risk_score_id: uuid.UUID
    
    model_name: str
    model_version: str
    feature_version: str
    dataset_version: str
    
    prediction_timestamp: datetime
    actual_risk: Optional[float] = None
    prediction_error: Optional[float] = None
    
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class AssetRiskForecastResponse(BaseModel):
    asset_id: uuid.UUID
    current_risk: float
    current_financial_exposure: Optional[float] = None
    
    forecasts: Dict[int, RiskPredictionRead] = Field(description="Key is horizon in days (e.g., 7, 30, 90)")
    drivers: List[PredictionDriver]
    
class OrganizationRiskForecastResponse(BaseModel):
    organization_id: uuid.UUID
    current_avg_risk: float
    current_total_financial_exposure: Optional[float] = None
    
    forecasts: Dict[int, RiskPredictionRead] = Field(description="Aggregated/derived predictions at the organization level")
    drivers: List[PredictionDriver]
    
class PredictionBulkResult(BaseModel):
    assets_processed: int
    predictions_generated: int
    insufficient_data: int
    failed: int
