import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any
from sqlalchemy import String, ForeignKey, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDMixin, get_utc_now

if TYPE_CHECKING:
    from app.models.organization import Organization


class ComplianceFramework(Base, UUIDMixin):
    """
    Standard compliance framework definition (e.g. NIST, ISO 27001).
    """
    __tablename__ = "compliance_frameworks"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    # Relationships
    compliance_controls: Mapped[list["ComplianceControl"]] = relationship(
        "ComplianceControl", back_populates="framework", cascade="all, delete-orphan"
    )


class ComplianceControl(Base, UUIDMixin):
    """
    Specific control or requirement within a compliance framework.
    """
    __tablename__ = "compliance_controls"

    framework_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_frameworks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    control_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    requirement_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    # Relationships
    framework: Mapped["ComplianceFramework"] = relationship(
        "ComplianceFramework", back_populates="compliance_controls"
    )
    control_assessments: Mapped[list["ControlAssessment"]] = relationship(
        "ControlAssessment", back_populates="compliance_control", cascade="all, delete-orphan"
    )


class ControlAssessment(Base, UUIDMixin):
    """
    Assessment of an organization's implementation of a specific compliance control.
    """
    __tablename__ = "control_assessments"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    compliance_control_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_controls.id", ondelete="CASCADE"), index=True, nullable=False
    )
    
    status: Mapped[str] = mapped_column(
        String(50), index=True, default="not_assessed", nullable=False
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    evidence: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    
    assessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assessed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="control_assessments")
    compliance_control: Mapped["ComplianceControl"] = relationship("ComplianceControl", back_populates="control_assessments")
