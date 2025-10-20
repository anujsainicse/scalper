from sqlalchemy import Column, String, Numeric, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import uuid
import enum


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class OrderType(str, enum.Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"


class OrderSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign Key to Bot
    bot_id = Column(UUID(as_uuid=True), ForeignKey("bots.id", ondelete="CASCADE"), nullable=False, index=True)

    # Exchange Order ID (from the exchange)
    exchange_order_id = Column(String(100), unique=True, nullable=True, index=True)

    # Order Details
    symbol = Column(String(20), nullable=False, index=True)  # e.g., "ETH/USDT"
    side = Column(SQLEnum(OrderSide), nullable=False)
    order_type = Column(SQLEnum(OrderType), nullable=False, default=OrderType.LIMIT)

    # Pricing and Quantity
    quantity = Column(Numeric(20, 8), nullable=False)
    price = Column(Numeric(20, 8), nullable=True)  # Nullable for market orders

    # Order Status
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)

    # Order Pairing (for tracking buy-sell cycles)
    paired_order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True, index=True)

    # Execution Details
    filled_quantity = Column(Numeric(20, 8), default=0, nullable=False)
    filled_price = Column(Numeric(20, 8), nullable=True)
    commission = Column(Numeric(20, 8), default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to Bot
    bot = relationship("Bot", back_populates="orders")

    def __repr__(self):
        return f"<Order(id={self.id}, symbol={self.symbol}, side={self.side}, status={self.status})>"
