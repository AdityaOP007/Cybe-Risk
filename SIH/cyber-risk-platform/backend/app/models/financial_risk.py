import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any
from sqlalchemy import String, ForeignKey, Float, DateTime, CheckConstraint, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDMixin, get_utc_now

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.asset import Asset
    from app.models.risk import RiskScore


class FinancialAssumption(Base, UUIDMixin):
    """
    Assumptions used to drive the financial risk models.
    """
    __tablename__ = "financial_assumptions"
    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 100", name="chk_financial_assumption_confidence"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Financial values often need exact precision; Numeric is suitable.
    value: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True) # e.g. "INR", "hours", "records"
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True) # e.g. "INR"
    
    source: Mapped[str] = mapped_column(String(255), default="organization_input", nullable=False)
    confidence: Mapped[int] = mapped_column(Float, default=100.0, nullable=False)
    
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    effective_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    organization: Mapped["Organization"] = relationship("Organization", backref="financial_assumptions")


class FinancialRiskAssessment(Base, UUIDMixin):
    """
    Financial Risk Assessment mapping cyber risk to financial impact.
    Immutable historical record.
    """
    __tablename__ = "financial_risk_assessments"
    __table_args__ = (
        CheckConstraint("potential_loss >= 0", name="chk_potential_loss"),
        CheckConstraint("expected_loss >= 0", name="chk_expected_loss"),
        CheckConstraint("confidence >= 0 AND confidence <= 100", name="chk_financial_risk_confidence"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), index=True, nullable=False
    )
    risk_score_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("risk_scores.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # Core Output Metrics
    potential_loss: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    expected_loss: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    annualized_expected_loss: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    
    # Detailed Breakdown (could be grouped into JSON, but explicit columns are useful for querying/analytics)
    direct_loss: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    data_loss: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    business_interruption_loss: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    recovery_loss: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    customer_impact: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    third_party_impact: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    regulatory_legal_exposure: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    fraud_loss: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    reputation_revenue_impact: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    
    confidence: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    data_completeness: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    calculation_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    assumptions_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, default=get_utc_now, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", backref="financial_risk_assessments")
    asset: Mapped["Asset"] = relationship("Asset", backref="financial_risk_assessments")
    risk_score: Mapped["RiskScore"] = relationship("RiskScore", backref="financial_risk_assessments")
