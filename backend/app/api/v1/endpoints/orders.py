"""
Orders API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.models.order import Order, OrderStatus, OrderSide
from app.schemas.order import OrderResponse, OrderStatistics
from app.services.trading.order_manager import OrderManager

router = APIRouter()


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    bot_id: Optional[UUID] = Query(None, description="Filter by bot ID"),
    exchange: Optional[str] = Query(None, description="Filter by exchange"),
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    side: Optional[OrderSide] = Query(None, description="Filter by side (BUY/SELL)"),
    status: Optional[OrderStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, le=1000, description="Maximum number of orders to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get orders with optional filtering.

    Query parameters:
    - bot_id: Filter orders by bot UUID
    - exchange: Filter by exchange name
    - ticker: Filter by trading pair
    - side: Filter by order side (BUY/SELL)
    - status: Filter by order status
    - limit: Maximum number of orders to return (max 1000)
    """
    query = select(Order)

    # Apply filters
    if bot_id:
        query = query.where(Order.bot_id == bot_id)

    if exchange:
        query = query.where(Order.exchange == exchange)

    if ticker:
        query = query.where(Order.ticker == ticker)

    if side:
        query = query.where(Order.side == side)

    if status:
        query = query.where(Order.status == status)

    # Order by most recent first
    query = query.order_by(Order.created_at.desc()).limit(limit)

    result = await db.execute(query)
    orders = result.scalars().all()

    # Add computed properties
    response_orders = []
    for order in orders:
        order_dict = {
            **{c.name: getattr(order, c.name) for c in order.__table__.columns},
            "fill_percentage": order.fill_percentage,
            "is_complete": order.is_complete
        }
        response_orders.append(order_dict)

    return response_orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific order by ID.
    """
    order_manager = OrderManager(db)
    order = await order_manager.get_order(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Return with computed properties
    return {
        **{c.name: getattr(order, c.name) for c in order.__table__.columns},
        "fill_percentage": order.fill_percentage,
        "is_complete": order.is_complete
    }


@router.get("/bot/{bot_id}/active", response_model=List[OrderResponse])
async def get_active_orders(
    bot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get active (non-completed) orders for a specific bot.

    Returns orders with status: PENDING, OPEN, or PARTIALLY_FILLED
    """
    order_manager = OrderManager(db)
    orders = await order_manager.get_active_orders(str(bot_id))

    # Add computed properties
    response_orders = []
    for order in orders:
        order_dict = {
            **{c.name: getattr(order, c.name) for c in order.__table__.columns},
            "fill_percentage": order.fill_percentage,
            "is_complete": order.is_complete
        }
        response_orders.append(order_dict)

    return response_orders


@router.get("/bot/{bot_id}/statistics", response_model=OrderStatistics)
async def get_order_statistics(
    bot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get order statistics for a specific bot.

    Returns:
    - Total number of orders
    - Number of filled, cancelled, failed, and active orders
    - Fill rate percentage
    - Total commission paid
    - Total trading volume
    """
    order_manager = OrderManager(db)
    stats = await order_manager.get_order_statistics(str(bot_id))

    return stats


@router.get("/bot/{bot_id}/history", response_model=List[OrderResponse])
async def get_order_history(
    bot_id: UUID,
    limit: int = Query(100, le=1000, description="Maximum number of orders to return"),
    status: Optional[OrderStatus] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get order history for a specific bot.

    Query parameters:
    - limit: Maximum number of orders to return (max 1000)
    - status: Filter by order status
    """
    order_manager = OrderManager(db)
    orders = await order_manager.get_bot_orders(
        bot_id=str(bot_id),
        limit=limit,
        status=status
    )

    # Add computed properties
    response_orders = []
    for order in orders:
        order_dict = {
            **{c.name: getattr(order, c.name) for c in order.__table__.columns},
            "fill_percentage": order.fill_percentage,
            "is_complete": order.is_complete
        }
        response_orders.append(order_dict)

    return response_orders


@router.get("/statistics/summary", response_model=OrderStatistics)
async def get_all_orders_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    Get order statistics across all bots.

    Returns aggregate statistics for all orders in the system.
    """
    # Get all orders
    result = await db.execute(
        select(Order).order_by(Order.created_at.desc()).limit(10000)
    )
    orders = result.scalars().all()

    # Calculate statistics
    total_orders = len(orders)
    filled_orders = len([o for o in orders if o.status == OrderStatus.FILLED])
    cancelled_orders = len([o for o in orders if o.status == OrderStatus.CANCELLED])
    failed_orders = len([o for o in orders if o.status == OrderStatus.FAILED])
    active_orders = len([o for o in orders if o.status in [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]])

    total_commission = sum(o.commission for o in orders if o.commission)
    total_volume = sum(o.quote_quantity for o in orders if o.quote_quantity)

    return OrderStatistics(
        total_orders=total_orders,
        filled_orders=filled_orders,
        cancelled_orders=cancelled_orders,
        failed_orders=failed_orders,
        active_orders=active_orders,
        fill_rate=(filled_orders / total_orders * 100) if total_orders > 0 else 0,
        total_commission=total_commission,
        total_volume=total_volume
    )
