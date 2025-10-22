"""Add cancellation_reason to orders table

Revision ID: 20250122_cancellation
Revises: 20251022_change_infinite_loop_default
Create Date: 2025-01-22 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250122_cancellation'
down_revision = '20251022_change_infinite_loop_default'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add cancellation_reason column to orders table

    This field tracks why an order was cancelled:
    - "UPDATE": Order cancelled as part of bot update (new order will be placed)
    - "STOP": Order cancelled when bot was stopped by user
    - "DELETE": Order cancelled when bot was deleted
    - "MANUAL": Order manually cancelled on exchange
    - NULL: Order cancelled but reason unknown (legacy or external)
    """
    op.add_column('orders',
        sa.Column('cancellation_reason', sa.String(50), nullable=True)
    )


def downgrade():
    """Remove cancellation_reason column from orders table"""
    op.drop_column('orders', 'cancellation_reason')
