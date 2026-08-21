"""sync incident application and system fields

Revision ID: b605e2e7f07e
Revises: be12be0839eb
Create Date: 2026-08-15 18:44:36.787744

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b605e2e7f07e"
down_revision: Union[str, Sequence[str], None] = "be12be0839eb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ==========================================================
    # INCIDENTS
    # ==========================================================

    op.add_column(
        "incidents",
        sa.Column(
            "created_by_system",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    # ==========================================================
    # SYSTEM METRICS
    # ==========================================================

    op.alter_column(
        "system_metrics",
        "application_id",
        existing_type=sa.UUID(),
        nullable=True,
    )


def downgrade() -> None:

    # Restore system_metrics.application_id as NOT NULL
    op.alter_column(
        "system_metrics",
        "application_id",
        existing_type=sa.UUID(),
        nullable=False,
    )

    # Remove created_by_system
    op.drop_column(
        "incidents",
        "created_by_system",
    )