"""add checks table

Revision ID: 6d647fa4d41a
Revises: f7f03ae5239f
Create Date: 2025-12-18
"""
from alembic import op
import sqlalchemy as sa

revision = "6d647fa4d41a"
down_revision = "f7f03ae5239f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "checks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("target_id", sa.Integer(), sa.ForeignKey("targets.id"), nullable=False),
        sa.Column("ok", sa.Boolean(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("error", sa.String(length=512), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_checks_target_id_checked_at", "checks", ["target_id", "checked_at"])


def downgrade() -> None:
    op.drop_index("ix_checks_target_id_checked_at", table_name="checks")
    op.drop_table("checks")