"""
Order Model

Tracks order lifecycle from placement to completion.
"""

from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from app.db.session import Base
import uuid
import enum


class OrderType(str, enum.Enum):
    """Order type"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"


class OrderStatus(str, enum.Enum):
    """Order status through its lifecycle"""
    PENDING = "PENDING"  # Order created but not yet sent to exchange
    OPEN = "OPEN"  # Order sent to exchange and waiting for fills
    PARTIALLY_FILLED = "PARTIALLY_FILLED"  # Order partially executed
    FILLED = "FILLED"  # Order completely filled
    CANCELLED = "CANCELLED"  # Order cancelled by user
    REJECTED = "REJECTED"  # Order rejected by exchange
    EXPIRED = "EXPIRED"  # Order expired (e.g., GTD orders)
    FAILED = "FAILED"  # Order failed due to technical issues


class OrderSide(str, enum.Enum):
    """Order side"""
    BUY = "BUY"
    SELL = "SELL"


class Order(Base):
    """
    Track individual orders placed on exchanges.

    This model stores the complete lifecycle of an order from creation
    to final execution status.
    """
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Related entities
    bot_id = Column(UUID(as_uuid=True), ForeignKey('bots.id'), nullable=False, index=True)

    # Exchange information
    exchange = Column(String(50), nullable=False, index=True)
    exchange_order_id = Column(String(100), nullable=True, index=True)  # ID from exchange

    # Order details
    ticker = Column(String(20), nullable=False, index=True)
    side = Column(SQLEnum(OrderSide), nullable=False, index=True)
    order_type = Column(SQLEnum(OrderType), nullable=False)

    # Quantities
    quantity = Column(Float, nullable=False)
    filled_quantity = Column(Float, default=0.0)
    remaining_quantity = Column(Float, nullable=True)

    # Prices
    price = Column(Float, nullable=True)  # Order price (null for market orders)
    average_fill_price = Column(Float, nullable=True)  # Average price of fills
    stop_price = Column(Float, nullable=True)  # For stop orders

    # Status tracking
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, index=True, nullable=False)

    # Financial details
    commission = Column(Float, default=0.0)  # Trading fees
    commission_asset = Column(String(20), nullable=True)  # Asset used for commission
    quote_quantity = Column(Float, nullable=True)  # Total value in quote currency

    # PnL (calculated after order completion)
    pnl = Column(Float, nullable=True)

    # Error handling
    error_message = Column(String(500), nullable=True)
    retry_count = Column(Float, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    sent_to_exchange_at = Column(DateTime(timezone=True), nullable=True)
    first_fill_at = Column(DateTime(timezone=True), nullable=True)
    last_fill_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Additional data (exchange-specific response, etc.)
    extra_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<Order(id={self.id}, ticker={self.ticker}, side={self.side}, status={self.status})>"

    @property
    def is_complete(self) -> bool:
        """Check if order is in a final state"""
        return self.status in [
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
            OrderStatus.FAILED
        ]

    @property
    def fill_percentage(self) -> float:
        """Calculate fill percentage"""
        if not self.quantity:
            return 0.0
        return (self.filled_quantity / self.quantity) * 100.0
