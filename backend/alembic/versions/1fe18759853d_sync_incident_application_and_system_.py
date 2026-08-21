"""sync incident application and system fields

Revision ID: 1fe18759853d
Revises: b605e2e7f07e
Create Date: 2026-08-15 18:44:45.070559

"""

from typing import Sequence, Union

from alembic import op


revision: str = "1fe18759853d"
down_revision: Union[str, Sequence[str], None] = "b605e2e7f07e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass