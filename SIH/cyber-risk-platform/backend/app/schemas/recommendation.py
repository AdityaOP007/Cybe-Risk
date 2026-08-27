import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any

class RecommendationRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    asset_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    priority: str
    estimated_cost: float | None = None
    expected_risk_reduction: float | None = None
    status: str
    generated_at: datetime
    accepted_at: datetime | None = None
    completed_at: datetime | None = None
    metadata_: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
