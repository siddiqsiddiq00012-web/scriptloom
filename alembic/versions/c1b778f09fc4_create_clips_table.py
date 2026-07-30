"""create clips table

Revision ID: c1b778f09fc4
Revises: 9029530c57c9
Create Date: 2026-07-24 22:35:47.511621
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c1b778f09fc4"
down_revision: Union[str, Sequence[str], None] = "9029530c57c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clips",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("media_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("start_time", sa.Integer(), nullable=False),
        sa.Column("end_time", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("output_path", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["media_id"],
            ["media.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_clips_id",
        "clips",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_clips_id",
        table_name="clips",
    )

    op.drop_table("clips")