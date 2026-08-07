from datetime import datetime, timezone
from sqlalchemy import Boolean, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
    )

    url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    secret: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    subscribed_events: Mapped[dict] = mapped_column(
        JSON,
        default=lambda: ["*"],  # list of event strings
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    deliveries = relationship(
        "WebhookDeliveryLog",
        backref="webhook_endpoint",
        cascade="all, delete-orphan",
    )


class WebhookDeliveryLog(Base):
    __tablename__ = "webhook_delivery_logs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    webhook_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("webhook_endpoints.id", ondelete="CASCADE"),
        index=True,
    )

    delivery_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    event_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    # status_code kept for backward-compatibility
    status_code: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    # attempts kept for backward-compatibility
    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",  # PENDING | PROCESSING | DELIVERED | FAILED
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    request_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    response_status: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )

    # Stored as canonical JSON string byte-for-byte
    payload_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    dispatch_timestamp: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


class DeadLetterQueue(Base):
    __tablename__ = "dead_letter_queue"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    delivery_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    failed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
