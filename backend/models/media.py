from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
    )

    filename: Mapped[str] = mapped_column(
        String(255),
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="uploaded",
    )

    duration: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    width: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    height: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    codec: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    bitrate: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    fps: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    project = relationship(
        "Project",
        back_populates="media",
    )

    clips = relationship(
        "Clip",
        back_populates="media",
        cascade="all, delete-orphan",
    )

    generated_assets = relationship(
        "GeneratedContent",
        back_populates="media",
        cascade="all, delete-orphan",
    )

    processing_jobs = relationship(
        "ProcessingJob",
        back_populates="media",
        cascade="all, delete-orphan",
    )