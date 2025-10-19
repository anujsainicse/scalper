"""
Models package

Import all models here so they are registered with SQLAlchemy's Base.metadata.
This is required for Alembic autogenerate to detect all tables.
"""

from app.models.bot import Bot, ActivityLog, Trade, TelegramConnection, BotStatus, OrderSide, Exchange
from app.models.credentials import ExchangeCredentials
from app.models.order import Order, OrderStatus, OrderType

__all__ = [
    'Bot',
    'ActivityLog',
    'Trade',
    'TelegramConnection',
    'BotStatus',
    'OrderSide',
    'Exchange',
    'ExchangeCredentials',
    'Order',
    'OrderStatus',
    'OrderType',
]
