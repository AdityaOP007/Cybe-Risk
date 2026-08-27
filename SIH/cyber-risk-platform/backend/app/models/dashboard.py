import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDMixin, TimestampMixin, get_utc_now

class DashboardAlert(Base, UUIDMixin):
    __tablename__ = "dashboard_alerts"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    source_module: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False) # critical, high, medium, low
    action_link: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False) # active, acknowledged, resolved, dismissed
    
    # Simple deduplication key
    fingerprint: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    
    first_seen: Mapped[datetime] = mapped_column(default=get_utc_now, nullable=False)
    last_seen: Mapped[datetime] = mapped_column(default=get_utc_now, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(nullable=True)


class ExecutiveInsight(Base, UUIDMixin):
    __tablename__ = "executive_insights"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    content: Mapped[str] = mapped_column(String, nullable=False)
    insight_type: Mapped[str] = mapped_column(String(50), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(default=get_utc_now, nullable=False)
