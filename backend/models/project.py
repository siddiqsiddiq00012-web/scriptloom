from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    name: Mapped[str] = mapped_column(
        String(255),
    )

    owner = relationship(
        "User",
        back_populates="projects",
    )

    media = relationship(
        "Media",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    clips = relationship(
        "Clip",
        back_populates="project",
        cascade="all, delete-orphan",
    )