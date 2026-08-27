import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any
from sqlalchemy import String, ForeignKey, DateTime, Integer, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDMixin, TimestampMixin, get_utc_now

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.asset import Asset
    from app.models.vulnerability import Vulnerability


class ThreatIntelligenceRecord(Base, UUIDMixin, TimestampMixin):
    """
    Global threat intelligence record (e.g. CVE, Campaign, Actor).
    Not tied to any specific organization to avoid duplication.
    """
    __tablename__ = "threat_intelligence_records"

    source: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    source_record_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    intelligence_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    
    severity: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True) # 0-100
    
    external_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    normalized_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    
    # Optional explicitly boolean flags for querying
    known_exploited: Mapped[bool] = mapped_column(default=False, server_default='false', index=True)
    
    indicators: Mapped[list["ThreatIndicator"]] = relationship(
        "ThreatIndicator", back_populates="threat_record", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_threat_intel_dedup", "source", "source_record_id", unique=True),
    )


class ThreatIndicator(Base, UUIDMixin, TimestampMixin):
    """
    Global Indicator of Compromise (IOC).
    """
    __tablename__ = "threat_indicators"

    threat_record_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("threat_intelligence_records.id", ondelete="CASCADE"), index=True, nullable=False
    )
    
    indicator_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False) # ipv4, domain, hash
    value: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    active: Mapped[bool] = mapped_column(default=True, server_default='true', index=True)
    
    metadata_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    threat_record: Mapped["ThreatIntelligenceRecord"] = relationship(
        "ThreatIntelligenceRecord", back_populates="indicators"
    )

    __table_args__ = (
        Index("ix_threat_indicator_dedup", "indicator_type", "value", unique=True),
    )


class ThreatCorrelation(Base, UUIDMixin):
    """
    Tenant-specific mapping of a Threat Intelligence Record to an Asset or Vulnerability.
    """
    __tablename__ = "threat_correlations"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    threat_record_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("threat_intelligence_records.id", ondelete="CASCADE"), index=True, nullable=False
    )
    
    asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), index=True, nullable=True
    )
    vulnerability_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vulnerabilities.id", ondelete="CASCADE"), index=True, nullable=True
    )
    
    correlation_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., vulnerability_match, indicator_match
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    
    metadata_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    threat_record: Mapped["ThreatIntelligenceRecord"] = relationship("ThreatIntelligenceRecord")
    asset: Mapped["Asset"] = relationship("Asset")
    vulnerability: Mapped["Vulnerability"] = relationship("Vulnerability")

    __table_args__ = (
        # Ensure we don't duplicate correlations between the exact same entity and threat
        Index(
            "ix_threat_corr_asset_dedup", 
            "organization_id", "threat_record_id", "asset_id", 
            unique=True, 
            postgresql_where="asset_id IS NOT NULL"
        ),
        Index(
            "ix_threat_corr_vuln_dedup", 
            "organization_id", "threat_record_id", "vulnerability_id", 
            unique=True, 
            postgresql_where="vulnerability_id IS NOT NULL"
        ),
    )
