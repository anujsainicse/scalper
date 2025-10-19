"""
Base classes and interfaces for exchange integrations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class OrderSide(Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderStatus(Enum):
    """Order status"""
    OPEN = "open"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PARTIALLY_FILLED = "partially_filled"


@dataclass
class OrderRequest:
    """Standardized order request across all exchanges"""
    symbol: str  # Standard format: "ETH/USDT"
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    leverage: Optional[int] = 1
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    time_in_force: str = "GTC"  # Good Till Cancel
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class OrderResponse:
    """Standardized order response"""
    order_id: str
    symbol: str
    side: OrderSide
    status: OrderStatus
    order_type: OrderType
    quantity: float
    filled_quantity: float
    price: Optional[float]
    average_price: Optional[float]
    timestamp: str
    exchange_specific: Optional[Dict[str, Any]] = None


@dataclass
class Position:
    """Standardized position representation"""
    symbol: str
    size: float  # positive for long, negative for short
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    leverage: int
    liquidation_price: Optional[float] = None


class BaseExchange(ABC):
    """
    Abstract base class for all exchange integrations.
    Each exchange adapter must implement these methods.
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize exchange client

        Args:
            api_key: Exchange API key
            api_secret: Exchange API secret
            testnet: Use testnet (default: False)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.exchange_name = self.__class__.__name__

    # ============= Abstract Methods (MUST IMPLEMENT) =============

    @abstractmethod
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """
        Place a new order

        Args:
            order: OrderRequest with order details

        Returns:
            OrderResponse with executed order details

        Raises:
            Exception: If order placement fails
        """
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an order

        Args:
            order_id: Exchange-specific order ID
            symbol: Trading pair symbol

        Returns:
            True if cancelled successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_order(self, order_id: str, symbol: str) -> OrderResponse:
        """
        Get order details

        Args:
            order_id: Exchange-specific order ID
            symbol: Trading pair symbol

        Returns:
            OrderResponse with order details

        Raises:
            ValueError: If order not found
        """
        pass

    @abstractmethod
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[OrderResponse]:
        """
        Get all open orders

        Args:
            symbol: Filter by symbol (optional)

        Returns:
            List of OrderResponse objects
        """
        pass

    @abstractmethod
    async def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get current position for a symbol

        Args:
            symbol: Trading pair symbol

        Returns:
            Position object or None if no position exists
        """
        pass

    @abstractmethod
    async def get_balance(self) -> Dict[str, float]:
        """
        Get account balance

        Returns:
            Dictionary with currency: balance pairs
        """
        pass

    @abstractmethod
    async def get_current_price(self, symbol: str) -> float:
        """
        Get current market price

        Args:
            symbol: Trading pair symbol

        Returns:
            Current price as float
        """
        pass

    @abstractmethod
    def normalize_symbol(self, symbol: str) -> str:
        """
        Convert standard symbol format to exchange-specific format

        Args:
            symbol: Standard format (e.g., "ETH/USDT")

        Returns:
            Exchange-specific format (e.g., "B-ETH_USDT" for CoinDCX)
        """
        pass

    @abstractmethod
    def denormalize_symbol(self, exchange_symbol: str) -> str:
        """
        Convert exchange-specific symbol to standard format

        Args:
            exchange_symbol: Exchange-specific format

        Returns:
            Standard format (e.g., "ETH/USDT")
        """
        pass

    # ============= Optional Methods (Can Override) =============

    async def close_position(self, symbol: str) -> OrderResponse:
        """
        Close entire position (default implementation using market order)

        Args:
            symbol: Trading pair symbol

        Returns:
            OrderResponse with close order details

        Raises:
            ValueError: If no position found
        """
        position = await self.get_position(symbol)
        if not position or position.size == 0:
            raise ValueError(f"No position found for {symbol}")

        # Determine order side (opposite of position)
        side = OrderSide.SELL if position.size > 0 else OrderSide.BUY

        order = OrderRequest(
            symbol=symbol,
            side=side,
            order_type=OrderType.MARKET,
            quantity=abs(position.size)
        )

        return await self.place_order(order)

    async def set_leverage(self, symbol: str, leverage: int) -> bool:
        """
        Set leverage for a symbol (exchange-specific, not all support)

        Args:
            symbol: Trading pair symbol
            leverage: Leverage multiplier

        Returns:
            True if successful

        Raises:
            NotImplementedError: If exchange doesn't support leverage change
        """
        raise NotImplementedError(
            f"{self.exchange_name} does not support changing leverage"
        )

    async def health_check(self) -> bool:
        """
        Check if exchange API is accessible

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            await self.get_balance()
            return True
        except Exception:
            return False

    def __str__(self) -> str:
        """String representation"""
        return f"{self.exchange_name}(testnet={self.testnet})"

    def __repr__(self) -> str:
        """Debug representation"""
        return f"<{self.exchange_name} testnet={self.testnet}>"
