import uuid
from typing import Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class NormalizedTelemetryEvent(BaseModel):
    """
    Canonical normalized representation of a telemetry event 
    after ingestion but before database storage.
    """
    organization_id: uuid.UUID
    asset_id: uuid.UUID | None = None
    source: str
    event_type: str
    severity: str
    message: str | None = None
    source_event_id: str | None = None
    occurred_at: datetime
    event_data: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)
