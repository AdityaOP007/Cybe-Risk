import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any

class ComplianceFrameworkRead(BaseModel):
    id: uuid.UUID
    name: str
    version: str | None = None
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ComplianceControlRead(BaseModel):
    id: uuid.UUID
    framework_id: uuid.UUID
    control_id: str
    title: str
    description: str | None = None
    category: str | None = None
    requirement_reference: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ControlAssessmentRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    compliance_control_id: uuid.UUID
    status: str
    score: float | None = None
    evidence: dict[str, Any] | None = None
    notes: str | None = None
    assessed_at: datetime | None = None
    assessed_by: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
