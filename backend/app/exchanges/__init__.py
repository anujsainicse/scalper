"""
Exchange adapters for different cryptocurrency exchanges.

This package provides a unified interface for interacting with multiple
cryptocurrency exchanges. Each exchange has its own adapter that implements
the BaseExchangeAdapter interface.
"""

from app.exchanges.base import BaseExchangeAdapter, OrderType, OrderStatus
from app.exchanges.factory import ExchangeFactory

__all__ = [
    'BaseExchangeAdapter',
    'OrderType',
    'OrderStatus',
    'ExchangeFactory',
]
