from datetime import datetime, timezone
from sqlalchemy import Float, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    media_id: Mapped[int] = mapped_column(
        ForeignKey("media.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )

    language: Mapped[str] = mapped_column(
        String(10),
        default="en",
    )

    full_text: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="completed",
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

    segments = relationship(
        "TranscriptSegment",
        back_populates="transcript",
        cascade="all, delete-orphan",
        order_by="TranscriptSegment.start_time",
    )


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    transcript_id: Mapped[int] = mapped_column(
        ForeignKey("transcripts.id", ondelete="CASCADE"),
        index=True,
    )

    speaker_label: Mapped[str] = mapped_column(
        String(50),
        default="Speaker 1",
    )

    start_time: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    end_time: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    text: Mapped[str] = mapped_column(
        Text,
    )

    chapter_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    key_assertion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    transcript = relationship(
        "Transcript",
        back_populates="segments",
    )
