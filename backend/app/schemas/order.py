"""
Pydantic schemas for Orders
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.order import OrderStatus, OrderType, OrderSide


class OrderBase(BaseModel):
    """Base order schema"""
    ticker: str = Field(..., description="Trading pair symbol")
    side: OrderSide = Field(..., description="Order side (BUY/SELL)")
    order_type: OrderType = Field(..., description="Order type (MARKET/LIMIT/etc)")
    quantity: float = Field(..., gt=0, description="Order quantity")
    price: Optional[float] = Field(None, gt=0, description="Order price (required for LIMIT orders)")
    stop_price: Optional[float] = Field(None, gt=0, description="Stop price (for STOP orders)")


class OrderCreate(OrderBase):
    """Schema for creating a new order"""
    bot_id: UUID = Field(..., description="Bot ID that placed this order")
    exchange: str = Field(..., description="Exchange name")


class OrderResponse(OrderBase):
    """Schema for returning order details"""
    id: UUID
    bot_id: UUID
    exchange: str
    exchange_order_id: Optional[str] = None
    status: OrderStatus
    filled_quantity: float
    remaining_quantity: Optional[float] = None
    average_fill_price: Optional[float] = None
    commission: float
    commission_asset: Optional[str] = None
    quote_quantity: Optional[float] = None
    pnl: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: float
    created_at: datetime
    updated_at: datetime
    sent_to_exchange_at: Optional[datetime] = None
    first_fill_at: Optional[datetime] = None
    last_fill_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    extra_data: Optional[Dict[str, Any]] = None

    # Computed properties
    fill_percentage: Optional[float] = Field(None, description="Percentage of order filled")
    is_complete: Optional[bool] = Field(None, description="Whether order is in a final state")

    class Config:
        from_attributes = True


class OrderStatistics(BaseModel):
    """Schema for order statistics"""
    total_orders: int
    filled_orders: int
    cancelled_orders: int
    failed_orders: int
    active_orders: int
    fill_rate: float = Field(..., description="Percentage of orders filled")
    total_commission: float
    total_volume: float


class OrderFilter(BaseModel):
    """Schema for filtering orders"""
    bot_id: Optional[UUID] = None
    exchange: Optional[str] = None
    ticker: Optional[str] = None
    side: Optional[OrderSide] = None
    status: Optional[OrderStatus] = None
    limit: int = Field(default=100, le=1000, description="Maximum number of orders to return")
