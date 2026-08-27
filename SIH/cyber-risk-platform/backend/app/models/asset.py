import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, Float, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.vulnerability import Vulnerability
    from app.models.telemetry import TelemetryEvent
    from app.models.risk import RiskScore
    from app.models.recommendation import Recommendation


class Asset(Base, UUIDMixin, TimestampMixin):
    """
    Asset entity representing a device, application, or resource.
    """
    __tablename__ = "assets"
    __table_args__ = (
        CheckConstraint("criticality >= 0 AND criticality <= 100", name="chk_asset_criticality"),
        CheckConstraint("business_value >= 0", name="chk_asset_business_value"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    asset_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    environment: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 0 to 100 scale
    criticality: Mapped[int] = mapped_column(Integer, index=True, default=0, nullable=False)
    business_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(100), nullable=True)
    operating_system: Mapped[str | None] = mapped_column(String(255), nullable=True)
    technology: Mapped[str | None] = mapped_column(String(255), nullable=True)
    internet_exposed: Mapped[bool] = mapped_column(Boolean, index=True, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), index=True, default="active", nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="assets"
    )
    vulnerabilities: Mapped[list["Vulnerability"]] = relationship(
        "Vulnerability", back_populates="asset", cascade="all, delete-orphan"
    )
    telemetry_events: Mapped[list["TelemetryEvent"]] = relationship(
        "TelemetryEvent", back_populates="asset"
    )
    risk_scores: Mapped[list["RiskScore"]] = relationship(
        "RiskScore", back_populates="asset", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", back_populates="asset", cascade="all, delete-orphan"
    )
