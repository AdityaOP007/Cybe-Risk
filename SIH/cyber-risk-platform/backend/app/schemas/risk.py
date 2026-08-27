import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any

class RiskScoreRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    asset_id: uuid.UUID | None = None
    score: float
    risk_level: str
    calculation_version: str | None = None
    metadata_: dict[str, Any] | None = None
    calculated_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
