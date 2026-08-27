import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Float, DateTime, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class Threat(Base, UUIDMixin, TimestampMixin):
    """
    Threat intelligence entity.
    """
    __tablename__ = "threats"
    __table_args__ = (
        CheckConstraint("threat_score >= 0 AND threat_score <= 100", name="chk_threat_score"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    threat_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    
    severity: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    threat_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    active: Mapped[bool] = mapped_column(Boolean, index=True, default=True, nullable=False)
    
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="threats")
