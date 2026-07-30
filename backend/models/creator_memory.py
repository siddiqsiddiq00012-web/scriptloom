from datetime import datetime, timezone
from sqlalchemy import ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class CreatorMemory(Base):
    __tablename__ = "creator_memories"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    media_id: Mapped[int | None] = mapped_column(
        ForeignKey("media.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        default="quote",  # quote | story | framework | analogy | customer_insight
    )

    quote_text: Mapped[str] = mapped_column(
        Text,
    )

    context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    embedding_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", backref="memories")
    media = relationship("Media", backref="memories")
