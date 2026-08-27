import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ThreatRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    threat_type: str
    description: str | None = None
    severity: str
    threat_score: float | None = None
    source: str | None = None
    external_reference: str | None = None
    active: bool
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
