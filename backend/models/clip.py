from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class Clip(Base):
    __tablename__ = "clips"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
    )

    media_id: Mapped[int] = mapped_column(
        ForeignKey("media.id", ondelete="CASCADE"),
    )

    title: Mapped[str] = mapped_column(
        String(255),
    )

    start_time: Mapped[float] = mapped_column(
        Float,
    )

    end_time: Mapped[float] = mapped_column(
        Float,
    )

    reason: Mapped[str] = mapped_column(
        String(1000),
    )

    output_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    subtitle_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    project = relationship(
        "Project",
        back_populates="clips",
    )

    media = relationship(
        "Media",
        back_populates="clips",
    )