import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any
from sqlalchemy import String, ForeignKey, Float, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDMixin, get_utc_now

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.asset import Asset


class RiskScore(Base, UUIDMixin):
    """
    Risk Score entity. Represents a point-in-time calculation of risk.
    Immutable historical record.
    """
    __tablename__ = "risk_scores"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="chk_risk_score"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), index=True, nullable=True
    )
    
    score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    
    calculation_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    risk_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, default=get_utc_now, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="risk_scores")
    asset: Mapped["Asset"] = relationship("Asset", back_populates="risk_scores")
