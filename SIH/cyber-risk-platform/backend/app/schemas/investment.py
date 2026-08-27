import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SecurityInvestmentRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None = None
    category: str
    cost: float
    expected_risk_reduction: float | None = None
    implementation_time_days: int | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
