from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.models.order import Order, OrderStatus
from app.models.bot import Bot
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
)

router = APIRouter()


@router.get("/", response_model=OrderListResponse)
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    bot_id: Optional[UUID] = None,
    status: Optional[OrderStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all orders with pagination and optional filtering by bot_id and status
    """
    # Build query
    query = select(Order)

    # Apply filters
    if bot_id:
        query = query.where(Order.bot_id == bot_id)
    if status:
        query = query.where(Order.status == status)

    # Get total count
    count_query = select(func.count(Order.id))
    if bot_id:
        count_query = count_query.where(Order.bot_id == bot_id)
    if status:
        count_query = count_query.where(Order.status == status)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())

    result = await db.execute(query)
    orders = result.scalars().all()

    return {
        "orders": orders,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific order by ID
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new order
    """
    # Verify bot exists
    bot_result = await db.execute(select(Bot).where(Bot.id == order_data.bot_id))
    bot = bot_result.scalar_one_or_none()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Create order
    order = Order(
        bot_id=order_data.bot_id,
        symbol=order_data.symbol,
        side=order_data.side,
        order_type=order_data.order_type,
        quantity=order_data.quantity,
        price=order_data.price,
        exchange_order_id=order_data.exchange_order_id,
    )

    db.add(order)
    await db.commit()
    await db.refresh(order)

    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: UUID,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an order (typically used to update status, filled_quantity, etc.)
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update order fields
    update_data = order_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)

    await db.commit()
    await db.refresh(order)

    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an order
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    await db.delete(order)
    await db.commit()

    return None
