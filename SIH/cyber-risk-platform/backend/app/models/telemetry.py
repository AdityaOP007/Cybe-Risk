import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any
from sqlalchemy import String, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDMixin, get_utc_now

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.asset import Asset


class TelemetryEvent(Base, UUIDMixin):
    """
    Telemetry event representing security logs/events from external sources.
    Immutable historical record.
    """
    __tablename__ = "telemetry_events"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"), index=True, nullable=True
    )
    
    source: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    message: Mapped[str | None] = mapped_column(String, nullable=True)
    
    event_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    
    source_event_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="telemetry_events"
    )
    asset: Mapped["Asset"] = relationship("Asset", back_populates="telemetry_events")

    __table_args__ = (
        Index(
            "ix_telemetry_dedup",
            "organization_id",
            "source",
            "source_event_id",
            unique=True,
            postgresql_where="source_event_id IS NOT NULL",
        ),
    )
