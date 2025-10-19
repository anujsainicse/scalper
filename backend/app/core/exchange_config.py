"""
Exchange configuration management
Loads exchange credentials from environment variables
"""

from pydantic import BaseModel
from typing import Optional
import os


class ExchangeConfig(BaseModel):
    """Configuration for an exchange"""
    api_key: str
    api_secret: str
    testnet: bool = False
    passphrase: Optional[str] = None  # Some exchanges (like OKX) need this


def get_exchange_config(exchange_name: str) -> ExchangeConfig:
    """
    Get exchange configuration from environment variables

    Environment variable naming pattern:
    - {EXCHANGE}_API_KEY
    - {EXCHANGE}_API_SECRET
    - {EXCHANGE}_TESTNET
    - {EXCHANGE}_PASSPHRASE (optional)

    Examples:
    - COINDCX_API_KEY, COINDCX_API_SECRET
    - BINANCE_API_KEY, BINANCE_API_SECRET
    - BYBIT_API_KEY, BYBIT_API_SECRET

    Args:
        exchange_name: Name of the exchange

    Returns:
        ExchangeConfig with credentials loaded from environment

    Raises:
        ValueError: If API credentials are missing
    """
    # Normalize exchange name for environment variables
    # "CoinDCX F" -> "COINDCX_F" -> "COINDCX"
    exchange_upper = exchange_name.upper().replace(' ', '_').replace('-', '_')

    # Try variations for common exchanges
    possible_names = [
        exchange_upper,
        exchange_upper.replace('_F', ''),  # CoinDCX_F -> COINDCX
        exchange_upper.replace('_FUTURES', ''),  # XXX_FUTURES -> XXX
    ]

    api_key = None
    api_secret = None
    testnet = False
    passphrase = None

    # Try to find credentials with any of the possible names
    for name in possible_names:
        api_key = os.getenv(f"{name}_API_KEY")
        api_secret = os.getenv(f"{name}_API_SECRET")

        if api_key and api_secret:
            # Found credentials, get other optional settings
            testnet = os.getenv(f"{name}_TESTNET", "false").lower() == "true"
            passphrase = os.getenv(f"{name}_PASSPHRASE")
            break

    if not api_key or not api_secret:
        raise ValueError(
            f"Missing API credentials for exchange '{exchange_name}'. "
            f"Please set {exchange_upper}_API_KEY and {exchange_upper}_API_SECRET "
            f"environment variables."
        )

    return ExchangeConfig(
        api_key=api_key,
        api_secret=api_secret,
        testnet=testnet,
        passphrase=passphrase
    )


def validate_exchange_config(exchange_name: str) -> bool:
    """
    Check if exchange configuration is available

    Args:
        exchange_name: Name of the exchange

    Returns:
        True if configuration is available, False otherwise
    """
    try:
        get_exchange_config(exchange_name)
        return True
    except ValueError:
        return False


def list_configured_exchanges() -> list[str]:
    """
    List all exchanges that have configuration available

    Returns:
        List of configured exchange names
    """
    common_exchanges = [
        'coindcx', 'binance', 'bybit', 'delta', 'okx', 'kraken', 'coinbase'
    ]

    configured = []
    for exchange in common_exchanges:
        if validate_exchange_config(exchange):
            configured.append(exchange)

    return configured
