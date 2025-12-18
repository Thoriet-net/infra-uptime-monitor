"""init targets

Revision ID: f7f03ae5239f
Revises:
Create Date: 2025-12-18
"""
from alembic import op
import sqlalchemy as sa

revision = "f7f03ae5239f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "targets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("target", sa.String(length=512), nullable=False),
        sa.Column("port", sa.Integer(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )


def downgrade() -> None:
    op.drop_table("targets")