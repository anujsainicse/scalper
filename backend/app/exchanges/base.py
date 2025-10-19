"""
Base Exchange Adapter

Defines the abstract interface that all exchange adapters must implement.
This ensures consistent behavior across different exchanges.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum
from decimal import Decimal


class OrderType(str, Enum):
    """Supported order types"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"


class OrderStatus(str, Enum):
    """Order execution status"""
    PENDING = "PENDING"
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


class OrderSide(str, Enum):
    """Order side"""
    BUY = "BUY"
    SELL = "SELL"


class BaseExchangeAdapter(ABC):
    """
    Abstract base class for exchange adapters.

    All exchange implementations must inherit from this class and implement
    all abstract methods. This ensures a consistent interface across exchanges.
    """

    def __init__(
        self,
        api_key: str,
        secret_key: str,
        testnet: bool = True,
        **kwargs
    ):
        """
        Initialize the exchange adapter.

        Args:
            api_key: Exchange API key
            secret_key: Exchange secret key
            testnet: Whether to use testnet (default: True)
            **kwargs: Additional exchange-specific parameters
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.testnet = testnet
        self.extra_params = kwargs

    @property
    @abstractmethod
    def exchange_name(self) -> str:
        """Return the exchange name"""
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate API credentials by making a test request.

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        pass

    @abstractmethod
    async def place_order(
        self,
        ticker: str,
        side: OrderSide,
        quantity: Decimal,
        order_type: OrderType = OrderType.LIMIT,
        price: Optional[Decimal] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Place an order on the exchange.

        Args:
            ticker: Trading pair symbol (e.g., 'ETH/USDT')
            side: Order side (BUY or SELL)
            quantity: Order quantity
            order_type: Type of order (MARKET, LIMIT, etc.)
            price: Order price (required for LIMIT orders)
            **kwargs: Additional order parameters

        Returns:
            Dict containing:
                - order_id: Exchange order ID
                - status: Order status
                - filled_quantity: Quantity filled
                - average_price: Average fill price
                - created_at: Order creation timestamp
                - raw_response: Raw exchange response
        """
        pass

    @abstractmethod
    async def cancel_order(
        self,
        order_id: str,
        ticker: str
    ) -> Dict[str, Any]:
        """
        Cancel an existing order.

        Args:
            order_id: Exchange order ID
            ticker: Trading pair symbol

        Returns:
            Dict containing cancellation confirmation
        """
        pass

    @abstractmethod
    async def get_order_status(
        self,
        order_id: str,
        ticker: str
    ) -> Dict[str, Any]:
        """
        Get the status of an order.

        Args:
            order_id: Exchange order ID
            ticker: Trading pair symbol

        Returns:
            Dict containing:
                - order_id: Exchange order ID
                - status: Current order status
                - filled_quantity: Quantity filled so far
                - remaining_quantity: Quantity remaining
                - average_price: Average fill price
                - updated_at: Last update timestamp
        """
        pass

    @abstractmethod
    async def get_balance(self, asset: str) -> Dict[str, Any]:
        """
        Get balance for a specific asset.

        Args:
            asset: Asset symbol (e.g., 'USDT', 'ETH')

        Returns:
            Dict containing:
                - asset: Asset symbol
                - free: Available balance
                - locked: Locked balance
                - total: Total balance
        """
        pass

    @abstractmethod
    async def get_market_price(self, ticker: str) -> Decimal:
        """
        Get current market price for a ticker.

        Args:
            ticker: Trading pair symbol (e.g., 'ETH/USDT')

        Returns:
            Decimal: Current market price
        """
        pass

    @abstractmethod
    async def get_ticker_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get detailed ticker information.

        Args:
            ticker: Trading pair symbol

        Returns:
            Dict containing:
                - symbol: Trading pair
                - min_quantity: Minimum order quantity
                - max_quantity: Maximum order quantity
                - price_precision: Number of decimal places for price
                - quantity_precision: Number of decimal places for quantity
                - min_notional: Minimum order value
        """
        pass

    async def get_open_orders(self, ticker: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of open orders.

        Args:
            ticker: Optional ticker to filter orders

        Returns:
            List of open orders
        """
        # Optional method - exchanges can override
        return []

    async def get_order_history(
        self,
        ticker: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get order history.

        Args:
            ticker: Optional ticker to filter orders
            limit: Maximum number of orders to return

        Returns:
            List of historical orders
        """
        # Optional method - exchanges can override
        return []

    def format_ticker(self, ticker: str) -> str:
        """
        Format ticker to exchange-specific format.

        Args:
            ticker: Standard ticker format (e.g., 'ETH/USDT')

        Returns:
            Exchange-specific ticker format
        """
        # Default implementation - exchanges can override
        return ticker.replace('/', '')

    async def close(self):
        """
        Close any open connections.

        Called when the adapter is no longer needed.
        """
        pass
