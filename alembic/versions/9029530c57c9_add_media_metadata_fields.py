"""add media metadata fields

Revision ID: 9029530c57c9
Revises: a74b5a4fe2d4
Create Date: 2026-07-24

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9029530c57c9"
down_revision: Union[str, Sequence[str], None] = "a74b5a4fe2d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "media",
        sa.Column("duration", sa.Float(), nullable=True),
    )

    op.add_column(
        "media",
        sa.Column("width", sa.Integer(), nullable=True),
    )

    op.add_column(
        "media",
        sa.Column("height", sa.Integer(), nullable=True),
    )

    op.add_column(
        "media",
        sa.Column("codec", sa.String(length=50), nullable=True),
    )

    op.add_column(
        "media",
        sa.Column("bitrate", sa.Integer(), nullable=True),
    )

    op.add_column(
        "media",
        sa.Column("fps", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("media", "fps")
    op.drop_column("media", "bitrate")
    op.drop_column("media", "codec")
    op.drop_column("media", "height")
    op.drop_column("media", "width")
    op.drop_column("media", "duration")