from datetime import datetime, timezone
from sqlalchemy import ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class VoiceDNA(Base):
    __tablename__ = "voice_dna"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )

    writing_style: Mapped[str] = mapped_column(
        String(100),
        default="Direct, authoritative B2B founder perspective",
    )

    tone: Mapped[str] = mapped_column(
        String(100),
        default="Authoritative & Conviction-driven",
    )

    vocabulary: Mapped[str] = mapped_column(
        Text,
        default="High domain authority, concise, data-backed assertions",
    )

    cta_style: Mapped[str] = mapped_column(
        String(255),
        default="Low-friction direct value offer",
    )

    hook_style: Mapped[str] = mapped_column(
        String(255),
        default="Counter-intuitive industry assertion or metric callout",
    )

    banned_words: Mapped[str] = mapped_column(
        Text,
        default="game-changer, synergy, paradigm shift, revolutionary, unleash, delve",
    )

    emoji_preference: Mapped[str] = mapped_column(
        String(50),
        default="minimal",
    )

    avg_sentence_length: Mapped[int] = mapped_column(
        Integer,
        default=14,
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

    user = relationship(
        "User",
        backref="voice_dna",
    )
