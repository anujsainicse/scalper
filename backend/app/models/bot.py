from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
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

    # Bot Configuration
    ticker = Column(String(20), nullable=False, index=True)
    exchange = Column(SQLEnum(Exchange), nullable=False)
    first_order = Column(SQLEnum(OrderSide), nullable=False)
    quantity = Column(Float, nullable=False)
    buy_price = Column(Float, nullable=False)
    sell_price = Column(Float, nullable=False)
    trailing_percent = Column(Float, nullable=True)
    infinite_loop = Column(Boolean, default=False)

    # Bot Status
    status = Column(SQLEnum(BotStatus), default=BotStatus.STOPPED, index=True)

    # Trading Metrics
    pnl = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    last_fill_time = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Additional metadata
    config = Column(JSON, nullable=True)  # For storing additional configuration

    def __repr__(self):
        return f"<Bot(id={self.id}, ticker={self.ticker}, status={self.status})>"


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    bot_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    level = Column(String(20), nullable=False, index=True)  # INFO, SUCCESS, WARNING, ERROR, TELEGRAM
    message = Column(String(500), nullable=False)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Additional metadata
    extra_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<ActivityLog(id={self.id}, level={self.level}, message={self.message[:50]})>"


class Trade(Base):
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
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

    def __repr__(self):
        return f"<Trade(id={self.id}, symbol={self.symbol}, side={self.side}, price={self.price})>"


class TelegramConnection(Base):
    __tablename__ = "telegram_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Telegram Info
    chat_id = Column(String(100), unique=True, nullable=False, index=True)
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

    def __repr__(self):
        return f"<TelegramConnection(id={self.id}, chat_id={self.chat_id}, username={self.username})>"
