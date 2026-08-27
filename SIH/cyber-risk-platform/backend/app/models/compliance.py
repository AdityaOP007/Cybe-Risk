import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any
from sqlalchemy import String, ForeignKey, Float, DateTime, Boolean, JSON, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDMixin, get_utc_now

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.control import SecurityControl


class ComplianceFramework(Base, UUIDMixin):
    """
    Standard compliance framework definition (e.g. NIST CSF, ISO 27001, RBI, SEBI).
    """
    __tablename__ = "compliance_frameworks"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    jurisdiction: Mapped[str | None] = mapped_column(String(100), nullable=True)
    effective_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    requirements: Mapped[list["ComplianceRequirement"]] = relationship(
        "ComplianceRequirement", back_populates="framework", cascade="all, delete-orphan"
    )


class ComplianceRequirement(Base, UUIDMixin):
    """
    Specific requirement within a framework.
    Supports a hierarchical structure using parent_requirement_id.
    """
    __tablename__ = "compliance_requirements"

    framework_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_frameworks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    requirement_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    parent_requirement_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("compliance_requirements.id", ondelete="SET NULL"), nullable=True
    )
    
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subcategory: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Requirement context
    applicability: Mapped[str | None] = mapped_column(String(100), nullable=True)
    requirement_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_reference: Mapped[str | None] = mapped_column(String, nullable=True)
    
    effective_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    
    metadata_: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    framework: Mapped["ComplianceFramework"] = relationship("ComplianceFramework", back_populates="requirements")
    children: Mapped[list["ComplianceRequirement"]] = relationship(
        "ComplianceRequirement", back_populates="parent", remote_side="[ComplianceRequirement.id]"
    )
    parent: Mapped["ComplianceRequirement"] = relationship(
        "ComplianceRequirement", back_populates="children", remote_side="[ComplianceRequirement.parent_requirement_id]"
    )


class ComplianceApplicability(Base, UUIDMixin):
    """
    Organization-specific override for whether a requirement applies to them.
    """
    __tablename__ = "compliance_applicability"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_requirements.id", ondelete="CASCADE"), index=True, nullable=False
    )
    
    # applicable, not_applicable, requires_review
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    rationale: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )


class ComplianceControlMapping(Base, UUIDMixin):
    """
    Many-to-Many mapping linking an organizational control to a compliance requirement.
    """
    __tablename__ = "compliance_control_mappings"

    framework_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_frameworks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_requirements.id", ondelete="CASCADE"), index=True, nullable=False
    )
    control_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("security_controls.id", ondelete="CASCADE"), index=True, nullable=False
    )
    
    # direct, partial, supporting, compensating, not_mapped
    mapping_type: Mapped[str] = mapped_column(String(50), default="direct", nullable=False)
    coverage_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    rationale: Mapped[str | None] = mapped_column(String, nullable=True)
    
    source: Mapped[str | None] = mapped_column(String(100), nullable=True) # manual, system, authoritative
    mapping_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )
    
    # Relationships
    requirement: Mapped["ComplianceRequirement"] = relationship()
    control: Mapped["SecurityControl"] = relationship()


class ComplianceEvidence(Base, UUIDMixin):
    """
    Evidence collected to support a mapped control.
    """
    __tablename__ = "compliance_evidence"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    control_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("security_controls.id", ondelete="CASCADE"), index=True, nullable=False
    )
    requirement_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("compliance_requirements.id", ondelete="SET NULL"), index=True, nullable=True
    )
    
    evidence_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="valid", nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    metadata_: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )


class ComplianceAssessment(Base, UUIDMixin):
    """
    The calculated assessment status of an organization against a specific requirement.
    """
    __tablename__ = "compliance_assessments"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    framework_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_frameworks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_requirements.id", ondelete="CASCADE"), index=True, nullable=False
    )
    
    # compliant, partially_compliant, non_compliant, not_assessed, not_applicable, insufficient_evidence, exception
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    
    coverage: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence_completeness: Mapped[float | None] = mapped_column(Float, nullable=True)
    control_effectiveness: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    assessment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    assessor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    calculation_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )
    
    # Relationships
    requirement: Mapped["ComplianceRequirement"] = relationship()


class ComplianceGap(Base, UUIDMixin):
    """
    Actionable gap discovered during an assessment.
    """
    __tablename__ = "compliance_gaps"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    framework_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_frameworks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_requirements.id", ondelete="CASCADE"), index=True, nullable=False
    )
    control_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("security_controls.id", ondelete="SET NULL"), index=True, nullable=True
    )
    asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"), index=True, nullable=True
    )
    
    gap_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    financial_exposure: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    description: Mapped[str] = mapped_column(String, nullable=False)
    evidence_gap: Mapped[str | None] = mapped_column(String, nullable=True)
    
    recommendation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("recommendations.id", ondelete="SET NULL"), nullable=True
    )
    
    # open, acknowledged, in_remediation, resolved, accepted, expired
    status: Mapped[str] = mapped_column(String(50), default="open", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )
    
    requirement: Mapped["ComplianceRequirement"] = relationship()
    control: Mapped["SecurityControl"] = relationship()


class ComplianceException(Base, UUIDMixin):
    """
    Formal exception to a compliance requirement.
    """
    __tablename__ = "compliance_exceptions"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_requirements.id", ondelete="CASCADE"), index=True, nullable=False
    )
    control_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("security_controls.id", ondelete="CASCADE"), index=True, nullable=True
    )
    
    reason: Mapped[str] = mapped_column(String, nullable=False)
    business_justification: Mapped[str] = mapped_column(String, nullable=False)
    risk_acceptance_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # requested, approved, rejected, expired, revoked
    status: Mapped[str] = mapped_column(String(50), default="requested", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
