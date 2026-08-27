import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any

class SimulationRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    scenario_type: str
    description: str | None = None
    asset_id: uuid.UUID | None = None
    parameters: dict[str, Any] | None = None
    results: dict[str, Any] | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
