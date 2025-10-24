"""add_performance_indexes

Revision ID: 002
Revises: 001
Create Date: 2025-01-24

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add indexes for better query performance

    # Bots table indexes
    op.create_index('ix_bots_status', 'bots', ['status'])
    op.create_index('ix_bots_exchange', 'bots', ['exchange'])
    op.create_index('ix_bots_ticker', 'bots', ['ticker'])
    op.create_index('ix_bots_created_at', 'bots', ['created_at'])

    # Orders table indexes
    op.create_index('ix_orders_bot_id', 'orders', ['bot_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    op.create_index('ix_orders_bot_id_status', 'orders', ['bot_id', 'status'])
    op.create_index('ix_orders_bot_id_created_at', 'orders', ['bot_id', 'created_at'])
    op.create_index('ix_orders_exchange_order_id', 'orders', ['exchange_order_id'])

    # Activity logs table indexes
    op.create_index('ix_activity_logs_bot_id', 'activity_logs', ['bot_id'])
    op.create_index('ix_activity_logs_level', 'activity_logs', ['level'])
    op.create_index('ix_activity_logs_timestamp', 'activity_logs', ['timestamp'])
    op.create_index('ix_activity_logs_bot_id_timestamp', 'activity_logs', ['bot_id', 'timestamp'])


def downgrade() -> None:
    # Remove indexes

    # Bots table indexes
    op.drop_index('ix_bots_status')
    op.drop_index('ix_bots_exchange')
    op.drop_index('ix_bots_ticker')
    op.drop_index('ix_bots_created_at')

    # Orders table indexes
    op.drop_index('ix_orders_bot_id')
    op.drop_index('ix_orders_status')
    op.drop_index('ix_orders_bot_id_status')
    op.drop_index('ix_orders_bot_id_created_at')
    op.drop_index('ix_orders_exchange_order_id')

    # Activity logs table indexes
    op.drop_index('ix_activity_logs_bot_id')
    op.drop_index('ix_activity_logs_level')
    op.drop_index('ix_activity_logs_timestamp')
    op.drop_index('ix_activity_logs_bot_id_timestamp')
