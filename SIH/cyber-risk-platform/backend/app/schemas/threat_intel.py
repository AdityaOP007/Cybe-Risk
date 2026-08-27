from datetime import datetime
from uuid import UUID
from typing import Any, Optional
from pydantic import BaseModel, Field


class ThreatIndicatorBase(BaseModel):
    indicator_type: str = Field(..., description="ipv4, ipv6, domain, url, hash_md5, hash_sha256, etc.")
    value: str = Field(..., description="The IOC value")
    confidence: Optional[int] = Field(None, ge=0, le=100)
    source: Optional[str] = None
    active: bool = True
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    metadata_data: dict[str, Any] = Field(default_factory=dict)


class ThreatIndicatorCreate(ThreatIndicatorBase):
    pass


class ThreatIndicatorResponse(ThreatIndicatorBase):
    id: UUID
    threat_record_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ThreatIntelligenceRecordBase(BaseModel):
    source: str
    source_record_id: str
    intelligence_type: str = Field(..., description="vulnerability, malware, campaign, actor")
    title: str
    description: Optional[str] = None
    severity: str = Field(..., description="informational, low, medium, high, critical")
    confidence: Optional[int] = Field(None, ge=0, le=100)
    external_reference: Optional[str] = None
    published_at: Optional[datetime] = None
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    known_exploited: bool = False
    raw_data: dict[str, Any] = Field(default_factory=dict)
    normalized_data: dict[str, Any] = Field(default_factory=dict)


class ThreatIntelligenceRecordCreate(ThreatIntelligenceRecordBase):
    indicators: list[ThreatIndicatorCreate] = Field(default_factory=list)


class ThreatIntelligenceRecordResponse(ThreatIntelligenceRecordBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    indicators: list[ThreatIndicatorResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class PaginatedThreatIntelligence(BaseModel):
    items: list[ThreatIntelligenceRecordResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class ThreatCorrelationBase(BaseModel):
    correlation_type: str
    confidence: int = Field(100, ge=0, le=100)
    reason: str
    detected_at: datetime
    metadata_data: dict[str, Any] = Field(default_factory=dict)


class ThreatCorrelationResponse(ThreatCorrelationBase):
    id: UUID
    organization_id: UUID
    threat_record_id: UUID
    asset_id: Optional[UUID] = None
    vulnerability_id: Optional[UUID] = None
    
    # We embed the threat record here to make it useful for the UI
    threat_record: Optional[ThreatIntelligenceRecordResponse] = None

    model_config = {"from_attributes": True}


class ThreatIntelligenceStats(BaseModel):
    total_threats: int
    known_exploited: int
    critical: int
    high: int
    medium: int
    low: int
    informational: int
    indicators: int
    by_source: dict[str, int]
    by_intelligence_type: dict[str, int]
