"""Analytics models for tracking visitors, referral sources, and Product Hunt launch metrics."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalyticsVisit(Base):
    """Stores anonymous telemetry on page visitors and referral sources."""

    __tablename__ = "analytics_visits"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    visitor_id: Mapped[str | None] = mapped_column(
        String(64),
        index=True,
        nullable=True,
    )
    source: Mapped[str] = mapped_column(
        String(64),
        index=True,
        default="direct",
        nullable=False,
    )
    ref: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    utm_source: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    utm_medium: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    utm_campaign: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    referrer: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    path: Mapped[str] = mapped_column(
        String(256),
        default="/",
        nullable=False,
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    ip_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
