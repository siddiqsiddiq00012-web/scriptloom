from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class ProgressEvent(Base):
    __tablename__ = "progress_events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    event_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    media_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=True,
    )

    correlation_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
        default="",
    )

    payload_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
