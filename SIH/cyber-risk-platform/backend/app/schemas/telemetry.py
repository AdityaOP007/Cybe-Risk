import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any

class TelemetryEventRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    asset_id: uuid.UUID | None = None
    source: str
    event_type: str
    severity: str
    message: str | None = None
    event_data: dict[str, Any]
    source_event_id: str | None = None
    occurred_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
