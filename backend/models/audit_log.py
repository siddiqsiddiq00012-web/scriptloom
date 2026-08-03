from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    request_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
        default="",
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=True,
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        default="",
    )

    action: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    resource: Mapped[str] = mapped_column(
        String(150),
        default="",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="SUCCESS",  # SUCCESS | FAILED | BLOCKED
    )

    metadata_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
