from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Enum as SQLEnum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import uuid
import enum


class BotStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


class OrderSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class Exchange(str, enum.Enum):
    COINDCX_F = "CoinDCX F"
    BINANCE = "Binance"


class Bot(Base):
    __tablename__ = "bots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # User Relationship (MULTI-USER SUPPORT)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Bot Configuration
    ticker = Column(String(20), nullable=False, index=True)
    exchange = Column(SQLEnum(Exchange), nullable=False)
    first_order = Column(SQLEnum(OrderSide), nullable=False)
    quantity = Column(Float, nullable=False)
    buy_price = Column(Float, nullable=False)
    sell_price = Column(Float, nullable=False)
    trailing_percent = Column(Float, nullable=True)
    leverage = Column(Integer, default=3)
    infinite_loop = Column(Boolean, default=True)

    # Bot Status
    status = Column(SQLEnum(BotStatus), default=BotStatus.STOPPED, index=True)

    # Trading Metrics
    pnl = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    last_fill_time = Column(DateTime(timezone=True), nullable=True)
    last_fill_side = Column(SQLEnum(OrderSide), nullable=True)
    last_fill_price = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Additional metadata
    config = Column(JSON, nullable=True)  # For storing additional configuration

    # Relationships
    user = relationship("User", back_populates="bots")
    orders = relationship("Order", back_populates="bot", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Bot(id={self.id}, user_id={self.user_id}, ticker={self.ticker}, status={self.status})>"


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # User Relationship (MULTI-USER SUPPORT)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    bot_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    level = Column(String(20), nullable=False, index=True)  # INFO, SUCCESS, WARNING, ERROR, TELEGRAM
    message = Column(String(500), nullable=False)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Additional metadata
    extra_data = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="activity_logs")

    def __repr__(self):
        return f"<ActivityLog(id={self.id}, user_id={self.user_id}, level={self.level}, message={self.message[:50]})>"


class Trade(Base):
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # User Relationship (MULTI-USER SUPPORT)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    bot_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Trade Details
    symbol = Column(String(20), nullable=False)
    side = Column(SQLEnum(OrderSide), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)

    # Trade Metrics
    pnl = Column(Float, nullable=True)
    commission = Column(Float, default=0.0)

    # Exchange Info
    exchange_order_id = Column(String(100), nullable=True)
    exchange = Column(SQLEnum(Exchange), nullable=False)

    # Timestamps
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Additional metadata
    extra_data = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="trades")

    def __repr__(self):
        return f"<Trade(id={self.id}, user_id={self.user_id}, symbol={self.symbol}, side={self.side}, price={self.price})>"


class TelegramConnection(Base):
    __tablename__ = "telegram_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # User Relationship (MULTI-USER SUPPORT)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Telegram Info
    chat_id = Column(String(100), nullable=False, index=True)  # Changed from unique to support multiple users
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    # Connection Info
    is_active = Column(Boolean, default=True, index=True)
    connection_code = Column(String(6), nullable=True, index=True)  # 6-digit code for initial connection
    code_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_notification_at = Column(DateTime(timezone=True), nullable=True)

    # Additional metadata
    extra_data = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="telegram_connections")

    def __repr__(self):
        return f"<TelegramConnection(id={self.id}, user_id={self.user_id}, chat_id={self.chat_id}, username={self.username})>"
