import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any
from sqlalchemy import String, ForeignKey, Float, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.asset import Asset
    from app.models.recommendation import Recommendation


class CybersecurityInvestment(Base, UUIDMixin, TimestampMixin):
    """
    An investment candidate generated from a Recommendation.
    """
    __tablename__ = "cybersecurity_investments"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    recommendation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("recommendations.id", ondelete="SET NULL"), index=True, nullable=True
    )
    asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"), index=True, nullable=True
    )
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    
    cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    cost_type: Mapped[str] = mapped_column(String(50), default="one_time") # one_time, annual
    annualized_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    implementation_effort: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    risk_reduction: Mapped[float | None] = mapped_column(Float, nullable=True)
    financial_reduction: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True) # 0-100
    priority: Mapped[str] = mapped_column(String(50), nullable=True)
    urgency: Mapped[str] = mapped_column(String(50), nullable=True)
    
    dependencies: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True) # List of UUIDs
    conflicts: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True) # List of UUIDs
    mandatory: Mapped[bool] = mapped_column(Boolean, default=False)
    
    status: Mapped[str] = mapped_column(String(50), index=True, default="candidate", nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[organization_id])
    asset: Mapped["Asset"] = relationship("Asset")
    recommendation: Mapped["Recommendation"] = relationship("Recommendation")


class OptimizationRun(Base, UUIDMixin, TimestampMixin):
    """
    A run of the optimization engine.
    """
    __tablename__ = "optimization_runs"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    
    budget: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    horizon_months: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    objective: Mapped[str] = mapped_column(String(50), default="balanced", nullable=False)
    
    # Weights
    risk_weight: Mapped[float] = mapped_column(Float, default=0.4)
    financial_weight: Mapped[float] = mapped_column(Float, default=0.3)
    criticality_weight: Mapped[float] = mapped_column(Float, default=0.15)
    urgency_weight: Mapped[float] = mapped_column(Float, default=0.10)
    confidence_weight: Mapped[float] = mapped_column(Float, default=0.05)
    
    optimization_status: Mapped[str] = mapped_column(String(50), nullable=False) # optimal, feasible, heuristic, infeasible, budget_insufficient
    
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    remaining_budget: Mapped[float] = mapped_column(Float, default=0.0)
    
    risk_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_reduction: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    financial_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    financial_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    financial_reduction: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    optimization_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    calculation_version: Mapped[str] = mapped_column(String(50), default="1.0")

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[organization_id])
    portfolios: Mapped[list["OptimizationPortfolio"]] = relationship("OptimizationPortfolio", back_populates="run", cascade="all, delete-orphan")


class OptimizationPortfolio(Base, UUIDMixin, TimestampMixin):
    """
    The specific investments selected in an OptimizationRun.
    """
    __tablename__ = "optimization_portfolios"

    optimization_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("optimization_runs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    
    selected_investments: Mapped[list[str]] = mapped_column(JSONB, nullable=False) # List of CybersecurityInvestment UUIDs
    
    # Store snapshot to avoid recalculating if investments are deleted
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    risk_reduction: Mapped[float | None] = mapped_column(Float, nullable=True)
    financial_reduction: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    portfolio_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True) # e.g. "why selected", "why not selected" lists

    run: Mapped["OptimizationRun"] = relationship("OptimizationRun", back_populates="portfolios")


class RiskScenario(Base, UUIDMixin, TimestampMixin):
    """
    Counterfactual scenario representing organization state post-investment.
    """
    __tablename__ = "risk_scenarios"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    optimization_portfolio_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("optimization_portfolios.id", ondelete="SET NULL"), nullable=True
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    
    investments_applied: Mapped[list[str]] = mapped_column(JSONB, nullable=False) # UUIDs
    
    risk_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    financial_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    financial_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    scenario_version: Mapped[str] = mapped_column(String(50), default="1.0")
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[organization_id])
