"""align clips table with model

Revision ID: align_clips_schema
Revises: c1b778f09fc4
Create Date: 2026-08-08 06:45:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "align_clips_schema"
down_revision: Union[str, Sequence[str], None] = "c8a6a01bde31"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the status column (not in the model)
    with op.batch_alter_table("clips", schema=None) as batch_op:
        try:
            batch_op.drop_column("status")
        except Exception:
            pass  # Column may not exist if table was created by create_all

    # Alter start_time and end_time from Integer to Float (double precision)
    with op.batch_alter_table("clips", schema=None) as batch_op:
        try:
            batch_op.alter_column(
                "start_time",
                existing_type=sa.Integer(),
                type_=sa.Float(),
                existing_nullable=False,
            )
        except Exception:
            pass
        try:
            batch_op.alter_column(
                "end_time",
                existing_type=sa.Integer(),
                type_=sa.Float(),
                existing_nullable=False,
            )
        except Exception:
            pass

    # Add missing columns: reason (NOT NULL) and subtitle_path (nullable)
    with op.batch_alter_table("clips", schema=None) as batch_op:
        try:
            batch_op.add_column(
                sa.Column("reason", sa.String(length=1000), nullable=True)
            )
            # Backfill existing rows with a default value before setting NOT NULL
            op.execute("UPDATE clips SET reason = '' WHERE reason IS NULL")
            with op.batch_alter_table("clips", schema=None) as batch_op2:
                batch_op2.alter_column(
                    "reason",
                    existing_type=sa.String(length=1000),
                    nullable=False,
                )
        except Exception:
            pass  # Column may already exist
        try:
            batch_op.add_column(
                sa.Column("subtitle_path", sa.String(length=500), nullable=True)
            )
        except Exception:
            pass  # Column may already exist


def downgrade() -> None:
    with op.batch_alter_table("clips", schema=None) as batch_op:
        try:
            batch_op.drop_column("subtitle_path")
        except Exception:
            pass
        try:
            batch_op.drop_column("reason")
        except Exception:
            pass
        try:
            batch_op.alter_column(
                "end_time",
                existing_type=sa.Float(),
                type_=sa.Integer(),
                existing_nullable=False,
            )
            batch_op.alter_column(
                "start_time",
                existing_type=sa.Float(),
                type_=sa.Integer(),
                existing_nullable=False,
            )
        except Exception:
            pass
        try:
            batch_op.add_column(
                sa.Column("status", sa.String(length=50), nullable=False)
            )
        except Exception:
            pass
