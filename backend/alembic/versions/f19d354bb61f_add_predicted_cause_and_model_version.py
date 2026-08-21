"""add predicted cause and model version

Revision ID: f19d354bb61f
Revises: 24644289ec07
Create Date: 2026-07-29 15:40:55.318962
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f19d354bb61f"
down_revision: Union[str, Sequence[str], None] = "24644289ec07"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ==========================
    # Evidence
    # ==========================

    op.add_column(
        "evidence",
        sa.Column(
            "pod_restart_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )

    op.add_column(
        "evidence",
        sa.Column(
            "deployment_changed",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )

    op.add_column(
        "evidence",
        sa.Column(
            "database_timeout_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )

    op.add_column(
        "evidence",
        sa.Column(
            "service_name",
            sa.String(100),
            server_default="unknown-service",
            nullable=False,
        ),
    )

    op.add_column(
        "evidence",
        sa.Column(
            "environment",
            sa.String(30),
            server_default="production",
            nullable=False,
        ),
    )

    # ==========================
    # Investigation
    # ==========================

    op.add_column(
        "investigations",
        sa.Column(
            "predicted_cause",
            sa.String(255),
            server_default="Unknown",
            nullable=False,
        ),
    )

    op.add_column(
        "investigations",
        sa.Column(
            "model_version",
            sa.String(30),
            server_default="v2",
            nullable=False,
        ),
    )

    op.alter_column(
        "investigations",
        "recommended_actions",
        existing_type=sa.TEXT(),
        nullable=True,
    )


def downgrade() -> None:

    op.alter_column(
        "investigations",
        "recommended_actions",
        existing_type=sa.TEXT(),
        nullable=False,
    )

    op.drop_column("investigations", "model_version")
    op.drop_column("investigations", "predicted_cause")

    op.drop_column("evidence", "environment")
    op.drop_column("evidence", "service_name")
    op.drop_column("evidence", "database_timeout_count")
    op.drop_column("evidence", "deployment_changed")
    op.drop_column("evidence", "pod_restart_count")