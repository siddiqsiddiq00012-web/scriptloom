from datetime import datetime, timezone
from sqlalchemy import Boolean, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

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

    status_code: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",  # PENDING | DELIVERED | FAILED | DEAD_LETTER
    )

    payload_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
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
