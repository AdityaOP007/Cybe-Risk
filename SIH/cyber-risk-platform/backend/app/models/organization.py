from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.telemetry import TelemetryEvent
    from app.models.threat import Threat
    from app.models.control import SecurityControl
    from app.models.risk import RiskScore
    from app.models.recommendation import Recommendation
    from app.models.compliance import ControlAssessment


class Organization(Base, UUIDMixin, TimestampMixin):
    """
    Organization entity representing a tenant in the system.
    """
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    organization_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    assets: Mapped[list["Asset"]] = relationship(
        "Asset", back_populates="organization", cascade="all, delete-orphan"
    )
    telemetry_events: Mapped[list["TelemetryEvent"]] = relationship(
        "TelemetryEvent", back_populates="organization", cascade="all, delete-orphan"
    )
    threats: Mapped[list["Threat"]] = relationship(
        "Threat", back_populates="organization", cascade="all, delete-orphan"
    )
    security_controls: Mapped[list["SecurityControl"]] = relationship(
        "SecurityControl", back_populates="organization", cascade="all, delete-orphan"
    )
    risk_scores: Mapped[list["RiskScore"]] = relationship(
        "RiskScore", back_populates="organization", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", back_populates="organization", cascade="all, delete-orphan"
    )
    control_assessments: Mapped[list["ControlAssessment"]] = relationship(
        "ControlAssessment", back_populates="organization", cascade="all, delete-orphan"
    )
