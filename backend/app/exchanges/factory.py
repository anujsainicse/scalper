"""
Exchange Factory

Factory pattern for creating exchange adapter instances.
Manages exchange adapter registration and instantiation.
"""

from typing import Dict, Type, Optional
from app.exchanges.base import BaseExchangeAdapter


class ExchangeFactory:
    """
    Factory for creating exchange adapters.

    Maintains a registry of available exchanges and provides methods
    to instantiate them with the appropriate credentials.
    """

    _adapters: Dict[str, Type[BaseExchangeAdapter]] = {}

    @classmethod
    def register(cls, exchange_name: str, adapter_class: Type[BaseExchangeAdapter]):
        """
        Register an exchange adapter.

        Args:
            exchange_name: Name of the exchange (e.g., 'coindcx', 'bybit')
            adapter_class: Exchange adapter class
        """
        cls._adapters[exchange_name.lower()] = adapter_class

    @classmethod
    def create(
        cls,
        exchange_name: str,
        api_key: str,
        secret_key: str,
        testnet: bool = True,
        **kwargs
    ) -> BaseExchangeAdapter:
        """
        Create an exchange adapter instance.

        Args:
            exchange_name: Name of the exchange
            api_key: Exchange API key
            secret_key: Exchange secret key
            testnet: Whether to use testnet
            **kwargs: Additional exchange-specific parameters

        Returns:
            BaseExchangeAdapter: Exchange adapter instance

        Raises:
            ValueError: If exchange is not registered
        """
        exchange_key = exchange_name.lower()

        if exchange_key not in cls._adapters:
            available = ', '.join(cls._adapters.keys())
            raise ValueError(
                f"Exchange '{exchange_name}' is not registered. "
                f"Available exchanges: {available}"
            )

        adapter_class = cls._adapters[exchange_key]
        return adapter_class(
            api_key=api_key,
            secret_key=secret_key,
            testnet=testnet,
            **kwargs
        )

    @classmethod
    def get_available_exchanges(cls) -> list[str]:
        """
        Get list of registered exchanges.

        Returns:
            List of exchange names
        """
        return list(cls._adapters.keys())

    @classmethod
    def is_supported(cls, exchange_name: str) -> bool:
        """
        Check if an exchange is supported.

        Args:
            exchange_name: Name of the exchange

        Returns:
            bool: True if exchange is registered
        """
        return exchange_name.lower() in cls._adapters


# Convenience function for creating adapters
def create_exchange_adapter(
    exchange_name: str,
    api_key: str,
    secret_key: str,
    testnet: bool = True,
    **kwargs
) -> BaseExchangeAdapter:
    """
    Create an exchange adapter instance.

    This is a convenience wrapper around ExchangeFactory.create()

    Args:
        exchange_name: Name of the exchange
        api_key: Exchange API key
        secret_key: Exchange secret key
        testnet: Whether to use testnet
        **kwargs: Additional exchange-specific parameters

    Returns:
        BaseExchangeAdapter: Exchange adapter instance
    """
    return ExchangeFactory.create(
        exchange_name=exchange_name,
        api_key=api_key,
        secret_key=secret_key,
        testnet=testnet,
        **kwargs
    )
