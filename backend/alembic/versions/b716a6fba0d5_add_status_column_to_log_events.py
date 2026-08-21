"""add status column to log_events

Revision ID: b716a6fba0d5
Revises: 9fee8966ced8
Create Date: 2026-07-31 20:30:44.137715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b716a6fba0d5'
down_revision: Union[str, Sequence[str], None] = '9fee8966ced8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum type ko explicitly yahan define karein
log_status_enum = sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'IGNORED', name='logstatusenum')


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Pehle Enum Type DB me create karein
    log_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Phir column add karein (server_default='PENDING' se existing rows me issue nahi ayega)
    op.add_column(
        'log_events', 
        sa.Column('status', log_status_enum, nullable=False, server_default='PENDING')
    )
    op.drop_column('log_events', 'processed')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('log_events', sa.Column('processed', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('log_events', 'status')

    # Downgrade ke waqt Enum Type ko bhi DB se drop karein
    log_status_enum.drop(op.get_bind(), checkfirst=True)