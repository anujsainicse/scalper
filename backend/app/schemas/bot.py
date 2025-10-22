from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class BotStatus(str, Enum):
    ACTIVE = "ACTIVE"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class Exchange(str, Enum):
    COINDCX_F = "CoinDCX F"
    BINANCE = "Binance"


class LogLevel(str, Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    TELEGRAM = "TELEGRAM"


# Bot Schemas
class BotBase(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    exchange: Exchange
    first_order: OrderSide
    quantity: float = Field(..., gt=0)
    buy_price: float = Field(..., gt=0)
    sell_price: float = Field(..., gt=0)
    trailing_percent: Optional[float] = Field(None, ge=0.1, le=3.0)
    leverage: Optional[int] = Field(3, ge=1, le=50)
    infinite_loop: bool = False

    @validator('sell_price')
    def sell_must_be_greater_than_buy(cls, v, values):
        if 'buy_price' in values and v <= values['buy_price']:
            raise ValueError('sell_price must be greater than buy_price')
        return v


class BotCreate(BotBase):
    pass


class BotUpdate(BaseModel):
    ticker: Optional[str] = Field(None, min_length=1, max_length=20)
    exchange: Optional[Exchange] = None
    first_order: Optional[OrderSide] = None
    quantity: Optional[float] = Field(None, gt=0)
    buy_price: Optional[float] = Field(None, gt=0)
    sell_price: Optional[float] = Field(None, gt=0)
    trailing_percent: Optional[float] = Field(None, ge=0.1, le=3.0)
    leverage: Optional[int] = Field(None, ge=1, le=50)
    infinite_loop: Optional[bool] = None
    status: Optional[BotStatus] = None


class BotResponse(BotBase):
    id: UUID
    status: BotStatus
    pnl: float
    total_trades: int
    last_fill_time: Optional[datetime]
    last_fill_side: Optional[OrderSide]
    last_fill_price: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Activity Log Schemas
class ActivityLogBase(BaseModel):
    level: LogLevel
    message: str = Field(..., min_length=1, max_length=500)
    bot_id: Optional[UUID] = None


class ActivityLogCreate(ActivityLogBase):
    pass


class ActivityLogResponse(ActivityLogBase):
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


# Trade Schemas
class TradeBase(BaseModel):
    bot_id: UUID
    symbol: str
    side: OrderSide
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    exchange: Exchange


class TradeCreate(TradeBase):
    exchange_order_id: Optional[str] = None
    pnl: Optional[float] = None
    commission: float = 0.0


class TradeResponse(TradeBase):
    id: UUID
    pnl: Optional[float]
    commission: float
    exchange_order_id: Optional[str]
    executed_at: datetime

    class Config:
        from_attributes = True


# Status Update Schema
class BotStatusUpdate(BaseModel):
    status: BotStatus


# Statistics Schema
class BotStatistics(BaseModel):
    total_bots: int
    active_bots: int
    stopped_bots: int
    total_pnl: float
    total_trades: int


# Telegram Connection Schemas
class TelegramConnectionBase(BaseModel):
    chat_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TelegramConnectionCreate(TelegramConnectionBase):
    connection_code: str = Field(..., min_length=6, max_length=6)


class TelegramConnectionResponse(TelegramConnectionBase):
    id: UUID
    is_active: bool
    connected_at: datetime
    last_notification_at: Optional[datetime]

    class Config:
        from_attributes = True


class TelegramStatus(BaseModel):
    connected: bool
    chat_id: Optional[str] = None
    username: Optional[str] = None
    connected_at: Optional[datetime] = None


class TelegramConnectionCodeResponse(BaseModel):
    connection_code: str
    expires_at: datetime
    message: str


class TelegramVerifyRequest(BaseModel):
    connection_code: str = Field(..., min_length=6, max_length=6)
    chat_id: str


class TelegramNotification(BaseModel):
    message: str
    level: Optional[LogLevel] = LogLevel.INFO
