import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str
    industry: str | None = None
    organization_type: str | None = None
    country: str | None = None
    description: str | None = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: str | None = None
    industry: str | None = None
    organization_type: str | None = None
    country: str | None = None
    description: str | None = None

class OrganizationRead(OrganizationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
