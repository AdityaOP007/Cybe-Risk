import uuid
from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress, field_validator
from typing import Any
from datetime import datetime
import re

class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    asset_type: str = Field(..., max_length=100)
    environment: str = Field(..., max_length=100)
    criticality: int = Field(default=0, ge=0, le=100)
    business_value: float = Field(default=0.0, ge=0.0)
    owner: str | None = Field(default=None, max_length=255)
    department: str | None = Field(default=None, max_length=255)
    hostname: str | None = Field(default=None, max_length=255)
    ip_address: IPvAnyAddress | str | None = None
    operating_system: str | None = Field(default=None, max_length=255)
    technology: str | None = Field(default=None, max_length=255)
    internet_exposed: bool = False
    status: str = Field(default="active", max_length=50)

    @field_validator("hostname")
    @classmethod
    def validate_hostname(cls, v: str | None) -> str | None:
        if v is not None:
            if not re.match(r"^[a-zA-Z0-9.-]+$", v):
                raise ValueError("Invalid hostname format")
        return v

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: Any) -> str | None:
        if v is not None:
            return str(v)
        return v


class AssetCreate(AssetBase):
    organization_id: uuid.UUID

class AssetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    asset_type: str | None = Field(default=None, max_length=100)
    environment: str | None = Field(default=None, max_length=100)
    criticality: int | None = Field(default=None, ge=0, le=100)
    business_value: float | None = Field(default=None, ge=0.0)
    owner: str | None = Field(default=None, max_length=255)
    department: str | None = Field(default=None, max_length=255)
    hostname: str | None = Field(default=None, max_length=255)
    ip_address: IPvAnyAddress | str | None = None
    operating_system: str | None = Field(default=None, max_length=255)
    technology: str | None = Field(default=None, max_length=255)
    internet_exposed: bool | None = None
    status: str | None = Field(default=None, max_length=50)

    @field_validator("hostname")
    @classmethod
    def validate_hostname(cls, v: str | None) -> str | None:
        if v is not None:
            if not re.match(r"^[a-zA-Z0-9.-]+$", v):
                raise ValueError("Invalid hostname format")
        return v

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: Any) -> str | None:
        if v is not None:
            return str(v)
        return v


class AssetRead(AssetBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PaginatedAssetsResponse(BaseModel):
    items: list[AssetRead]
    page: int
    page_size: int
    total: int
    total_pages: int


class AssetPostureResponse(BaseModel):
    asset_id: uuid.UUID
    asset_name: str
    criticality: int
    internet_exposed: bool
    open_vulnerabilities: int
    critical_vulnerabilities: int
    recent_telemetry_events: int
