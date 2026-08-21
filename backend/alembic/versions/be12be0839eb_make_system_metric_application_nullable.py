"""make system metric application nullable

Revision ID: be12be0839eb
Revises: 5e698383368f
Create Date: 2026-08-15 18:34:43.212661

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "be12be0839eb"
down_revision: Union[str, Sequence[str], None] = "5e698383368f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Allow server-wide metrics to have no application.
    """

    op.alter_column(
        "system_metrics",
        "application_id",
        existing_type=sa.UUID(),
        nullable=True,
    )


def downgrade() -> None:
    """
    Restore application_id as NOT NULL.
    """

    op.alter_column(
        "system_metrics",
        "application_id",
        existing_type=sa.UUID(),
        nullable=False,
    )