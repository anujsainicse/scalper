"""change_infinite_loop_default_to_true

Revision ID: 20251022_infinite_loop
Revises: 20251019_add_orders
Create Date: 2025-10-22 10:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20251022_infinite_loop'
down_revision: Union[str, None] = '20251019_add_orders'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Change the default value of infinite_loop column from False to True
    This only affects NEW rows created after this migration
    Existing rows retain their current values
    """
    # Alter column default using raw SQL for PostgreSQL
    op.execute("""
        ALTER TABLE bots
        ALTER COLUMN infinite_loop SET DEFAULT TRUE
    """)


def downgrade() -> None:
    """
    Revert the default value of infinite_loop column back to False
    """
    op.execute("""
        ALTER TABLE bots
        ALTER COLUMN infinite_loop SET DEFAULT FALSE
    """)
