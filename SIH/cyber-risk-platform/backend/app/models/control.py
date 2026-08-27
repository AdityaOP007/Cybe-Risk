import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Float, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class SecurityControl(Base, UUIDMixin, TimestampMixin):
    """
    Security Control entity representing a mitigation or safeguard.
    """
    __tablename__ = "security_controls"
    __table_args__ = (
        CheckConstraint(
            "coverage_percentage >= 0 AND coverage_percentage <= 100",
            name="chk_control_coverage"
        ),
        CheckConstraint(
            "effectiveness_percentage >= 0 AND effectiveness_percentage <= 100",
            name="chk_control_effectiveness"
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    
    control_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    
    coverage_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    effectiveness_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), index=True, default="active", nullable=False)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Module 11 fields
    implementation_status: Mapped[str] = mapped_column(String(50), default="unknown", nullable=False)
    
    implementation_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_assessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="security_controls")
