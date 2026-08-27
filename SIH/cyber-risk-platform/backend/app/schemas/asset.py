import uuid
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class AssetBase(BaseModel):
    name: str
    description: str | None = None
    asset_type: str
    environment: str
    criticality: int = Field(default=0, ge=0, le=100)
    business_value: float = Field(default=0.0, ge=0.0)
    owner: str | None = None
    department: str | None = None
    hostname: str | None = None
    ip_address: str | None = None
    operating_system: str | None = None
    technology: str | None = None
    internet_exposed: bool = False
    status: str = "active"

class AssetCreate(AssetBase):
    organization_id: uuid.UUID

class AssetUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    asset_type: str | None = None
    environment: str | None = None
    criticality: int | None = Field(default=None, ge=0, le=100)
    business_value: float | None = Field(default=None, ge=0.0)
    owner: str | None = None
    department: str | None = None
    hostname: str | None = None
    ip_address: str | None = None
    operating_system: str | None = None
    technology: str | None = None
    internet_exposed: bool | None = None
    status: str | None = None

class AssetRead(AssetBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
