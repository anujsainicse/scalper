"""
Exchange factory and registry for managing multiple exchange integrations
"""

from typing import Dict, Type, Optional, List
from app.exchanges.base import BaseExchange


class ExchangeRegistry:
    """
    Registry to manage all available exchange adapters.
    Uses decorator pattern to register exchanges.
    """

    _exchanges: Dict[str, Type[BaseExchange]] = {}

    @classmethod
    def register(cls, *names: str):
        """
        Decorator to register an exchange with one or more names

        Usage:
            @ExchangeRegistry.register("coindcx", "coindcx_futures")
            class CoinDCXAdapter(BaseExchange):
                pass

        Args:
            *names: One or more names to register the exchange under
        """
        def decorator(exchange_class: Type[BaseExchange]):
            for name in names:
                cls._exchanges[name.lower()] = exchange_class
            return exchange_class
        return decorator

    @classmethod
    def get_exchange(cls, name: str) -> Optional[Type[BaseExchange]]:
        """
        Get an exchange class by name

        Args:
            name: Exchange name (case-insensitive)

        Returns:
            Exchange class or None if not found
        """
        return cls._exchanges.get(name.lower())

    @classmethod
    def list_exchanges(cls) -> List[str]:
        """
        List all registered exchange names

        Returns:
            List of exchange names
        """
        return list(cls._exchanges.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if an exchange is registered

        Args:
            name: Exchange name

        Returns:
            True if registered, False otherwise
        """
        return name.lower() in cls._exchanges


class ExchangeFactory:
    """Factory to create exchange instances with proper configuration"""

    @staticmethod
    async def create(
        exchange_name: str,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = False
    ) -> BaseExchange:
        """
        Create an exchange instance

        Args:
            exchange_name: Name of the exchange (e.g., 'coindcx', 'binance')
            api_key: API key (optional, will load from config if not provided)
            api_secret: API secret (optional, will load from config if not provided)
            testnet: Use testnet (default: False)

        Returns:
            Initialized exchange instance

        Raises:
            ValueError: If exchange is not found or configuration is missing
        """
        # Get exchange class from registry
        exchange_class = ExchangeRegistry.get_exchange(exchange_name)

        if not exchange_class:
            available = ExchangeRegistry.list_exchanges()
            raise ValueError(
                f"Exchange '{exchange_name}' not found. "
                f"Available exchanges: {', '.join(available)}"
            )

        # Load config if credentials not provided
        if api_key is None or api_secret is None:
            from app.core.exchange_config import get_exchange_config
            config = get_exchange_config(exchange_name)
            api_key = api_key or config.api_key
            api_secret = api_secret or config.api_secret
            testnet = config.testnet

        # Create and return instance
        return exchange_class(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet
        )

    @staticmethod
    def create_sync(
        exchange_name: str,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = False
    ) -> BaseExchange:
        """
        Synchronous version of create() for non-async contexts

        Args:
            exchange_name: Name of the exchange
            api_key: API key (optional)
            api_secret: API secret (optional)
            testnet: Use testnet (default: False)

        Returns:
            Initialized exchange instance
        """
        exchange_class = ExchangeRegistry.get_exchange(exchange_name)

        if not exchange_class:
            available = ExchangeRegistry.list_exchanges()
            raise ValueError(
                f"Exchange '{exchange_name}' not found. "
                f"Available exchanges: {', '.join(available)}"
            )

        if api_key is None or api_secret is None:
            from app.core.exchange_config import get_exchange_config
            config = get_exchange_config(exchange_name)
            api_key = api_key or config.api_key
            api_secret = api_secret or config.api_secret
            testnet = config.testnet

        return exchange_class(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet
        )


# Export main classes
__all__ = [
    'BaseExchange',
    'ExchangeRegistry',
    'ExchangeFactory',
    'OrderSide',
    'OrderType',
    'OrderStatus',
    'OrderRequest',
    'OrderResponse',
    'Position'
]

# Re-export from base for convenience
from app.exchanges.base import (
    OrderSide,
    OrderType,
    OrderStatus,
    OrderRequest,
    OrderResponse,
    Position
)

# Import adapters to trigger registration
from app.exchanges.coindcx import CoinDCXAdapter
