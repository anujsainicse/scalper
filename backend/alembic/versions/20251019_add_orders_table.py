"""add_orders_table

Revision ID: 20251019_add_orders
Revises: fef8185d3887
Create Date: 2025-10-19 17:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251019_add_orders'
down_revision: Union[str, None] = 'fef8185d3887'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create OrderStatus enum
    op.execute("""
        CREATE TYPE orderstatus AS ENUM (
            'PENDING', 'FILLED', 'PARTIALLY_FILLED', 'CANCELLED', 'FAILED'
        )
    """)

    # Create OrderType enum
    op.execute("""
        CREATE TYPE ordertype AS ENUM ('LIMIT', 'MARKET')
    """)

    # Create OrderSide enum (if not already exists from bot model)
    # Note: This may fail if OrderSide already exists, which is fine
    try:
        op.execute("""
            CREATE TYPE orderside AS ENUM ('BUY', 'SELL')
        """)
    except:
        pass

    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('bot_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('exchange_order_id', sa.String(100), unique=True, nullable=True, index=True),
        sa.Column('symbol', sa.String(20), nullable=False, index=True),
        sa.Column('side', sa.Enum('BUY', 'SELL', name='orderside'), nullable=False),
        sa.Column('order_type', sa.Enum('LIMIT', 'MARKET', name='ordertype'), nullable=False),
        sa.Column('quantity', sa.Numeric(20, 8), nullable=False),
        sa.Column('price', sa.Numeric(20, 8), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'FILLED', 'PARTIALLY_FILLED', 'CANCELLED', 'FAILED', name='orderstatus'), nullable=False, index=True),
        sa.Column('filled_quantity', sa.Numeric(20, 8), nullable=False, server_default='0'),
        sa.Column('filled_price', sa.Numeric(20, 8), nullable=True),
        sa.Column('commission', sa.Numeric(20, 8), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Add foreign key constraint
    op.create_foreign_key(
        'orders_bot_id_fkey',
        'orders', 'bots',
        ['bot_id'], ['id'],
        ondelete='CASCADE'
    )

    # Create indexes
    op.create_index('ix_orders_id', 'orders', ['id'])
    op.create_index('ix_orders_bot_id', 'orders', ['bot_id'])
    op.create_index('ix_orders_symbol', 'orders', ['symbol'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    op.create_index('ix_orders_created_at', 'orders', ['created_at'])
    op.create_index('ix_orders_exchange_order_id', 'orders', ['exchange_order_id'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_orders_exchange_order_id', 'orders')
    op.drop_index('ix_orders_created_at', 'orders')
    op.drop_index('ix_orders_status', 'orders')
    op.drop_index('ix_orders_symbol', 'orders')
    op.drop_index('ix_orders_bot_id', 'orders')
    op.drop_index('ix_orders_id', 'orders')

    # Drop foreign key
    op.drop_constraint('orders_bot_id_fkey', 'orders', type_='foreignkey')

    # Drop table
    op.drop_table('orders')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS orderstatus')
    op.execute('DROP TYPE IF EXISTS ordertype')
    # Note: Not dropping orderside as it may be used by bots table
