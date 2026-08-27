import uuid
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Any

class TelemetryEventBase(BaseModel):
    source: str = Field(..., description="The telemetry source, e.g. siem, edr")
    event_type: str = Field(..., description="Normalized event type")
    severity: str = Field(..., description="Severity level")
    message: str | None = None
    event_data: dict[str, Any] = Field(default_factory=dict)
    source_event_id: str | None = None
    occurred_at: datetime | None = None

class TelemetryEventCreate(TelemetryEventBase):
    organization_id: uuid.UUID
    asset_id: uuid.UUID | None = None

class TelemetryEventRead(TelemetryEventBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    asset_id: uuid.UUID | None = None
    occurred_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TelemetryEventBatch(BaseModel):
    events: list[TelemetryEventCreate] = Field(..., max_length=1000)

class TelemetryBatchResult(BaseModel):
    total: int
    accepted: int
    rejected: int
    errors: list[dict[str, Any]]

class PaginatedTelemetry(BaseModel):
    items: list[TelemetryEventRead]
    page: int
    page_size: int
    total: int
    total_pages: int

class TelemetryStats(BaseModel):
    total_events: int
    critical_events: int
    high_events: int
    medium_events: int
    low_events: int
    informational_events: int
    by_source: dict[str, int]
    by_event_type: dict[str, int]
