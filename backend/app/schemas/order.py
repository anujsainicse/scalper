from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum
from decimal import Decimal


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


# Order Schemas
class OrderBase(BaseModel):
    bot_id: UUID
    symbol: str = Field(..., min_length=1, max_length=20)
    side: OrderSide
    order_type: OrderType
    quantity: Decimal = Field(..., gt=0)
    price: Optional[Decimal] = Field(None, gt=0)


class OrderCreate(OrderBase):
    exchange_order_id: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    exchange_order_id: Optional[str] = None
    filled_quantity: Optional[Decimal] = Field(None, ge=0)
    filled_price: Optional[Decimal] = Field(None, gt=0)
    commission: Optional[Decimal] = Field(None, ge=0)


class OrderResponse(OrderBase):
    id: UUID
    exchange_order_id: Optional[str]
    status: OrderStatus
    filled_quantity: Decimal
    filled_price: Optional[Decimal]
    commission: Decimal
    cancellation_reason: Optional[str] = None  # "UPDATE", "STOP", "DELETE", "MANUAL", None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Pagination
class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int
    page: int
    page_size: int
