import uuid
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class SecurityControlBase(BaseModel):
    name: str
    description: str | None = None
    control_type: str
    coverage_percentage: float | None = Field(default=None, ge=0.0, le=100.0)
    effectiveness_percentage: float | None = Field(default=None, ge=0.0, le=100.0)
    status: str = "active"
    owner: str | None = None
    implementation_date: datetime | None = None
    last_assessed_at: datetime | None = None

class SecurityControlCreate(SecurityControlBase):
    organization_id: uuid.UUID

class SecurityControlRead(SecurityControlBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
