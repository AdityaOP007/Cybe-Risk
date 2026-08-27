import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Float, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class SecurityInvestment(Base, UUIDMixin, TimestampMixin):
    """
    Security Investment entity for budget optimization.
    """
    __tablename__ = "security_investments"
    __table_args__ = (
        CheckConstraint("cost >= 0", name="chk_investment_cost"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    
    cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    expected_risk_reduction: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    implementation_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), index=True, default="proposed", nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="investments")
