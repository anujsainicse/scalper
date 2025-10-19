"""
Order Manager

Manages order lifecycle and database operations.
"""

from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.models.order import Order, OrderStatus, OrderType, OrderSide


class OrderManager:
    """
    Manages order lifecycle tracking and database operations.

    Responsibilities:
    - Create orders in database
    - Update order status from exchange responses
    - Track order fills and completion
    - Calculate fill percentages
    - Query order history
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(
        self,
        bot_id: str,
        exchange: str,
        ticker: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: Decimal,
        price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None
    ) -> Order:
        """
        Create a new order in the database.

        Args:
            bot_id: Bot UUID
            exchange: Exchange name
            ticker: Trading pair symbol
            side: Order side (BUY/SELL)
            order_type: Order type (MARKET/LIMIT/etc)
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            stop_price: Stop price (for STOP orders)

        Returns:
            Created Order instance
        """
        order = Order(
            bot_id=uuid.UUID(bot_id),
            exchange=exchange,
            ticker=ticker,
            side=side,
            order_type=order_type,
            quantity=float(quantity),
            price=float(price) if price else None,
            stop_price=float(stop_price) if stop_price else None,
            remaining_quantity=float(quantity),
            status=OrderStatus.PENDING
        )

        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def update_order_from_exchange(
        self,
        order_id: uuid.UUID,
        exchange_response: Dict[str, Any]
    ) -> Order:
        """
        Update order based on exchange API response.

        Args:
            order_id: Order UUID
            exchange_response: Response from exchange API

        Returns:
            Updated Order instance
        """
        # Get order from database
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one()

        # Extract data from exchange response
        exchange_order_id = exchange_response.get('order_id')
        status = exchange_response.get('status')
        filled_quantity = exchange_response.get('filled_quantity', 0)
        average_price = exchange_response.get('average_price') or exchange_response.get('average_fill_price')
        commission = exchange_response.get('commission', 0)
        commission_asset = exchange_response.get('commission_asset')
        error_message = exchange_response.get('error')

        # Update order fields
        if exchange_order_id:
            order.exchange_order_id = str(exchange_order_id)

        if status:
            old_status = order.status
            order.status = status

            # Update timestamps based on status changes
            if old_status == OrderStatus.PENDING and status in [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED]:
                order.sent_to_exchange_at = datetime.now()

            if status in [OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED] and not order.first_fill_at:
                order.first_fill_at = datetime.now()

            if status == OrderStatus.FILLED:
                order.last_fill_at = datetime.now()
                order.completed_at = datetime.now()

            if status in [OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.EXPIRED, OrderStatus.FAILED]:
                order.completed_at = datetime.now()

        if filled_quantity:
            order.filled_quantity = float(filled_quantity)
            order.remaining_quantity = order.quantity - float(filled_quantity)

        if average_price:
            order.average_fill_price = float(average_price)

        if commission:
            order.commission = float(commission)

        if commission_asset:
            order.commission_asset = commission_asset

        if error_message:
            order.error_message = error_message

        # Calculate quote quantity if we have fill data
        if order.average_fill_price and order.filled_quantity:
            order.quote_quantity = order.average_fill_price * order.filled_quantity

        # Store full response in extra_data
        order.extra_data = exchange_response

        # Update timestamp
        order.updated_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def get_order(self, order_id: uuid.UUID) -> Optional[Order]:
        """
        Get order by ID.

        Args:
            order_id: Order UUID

        Returns:
            Order instance or None
        """
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    async def get_bot_orders(
        self,
        bot_id: str,
        limit: int = 100,
        status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """
        Get orders for a specific bot.

        Args:
            bot_id: Bot UUID
            limit: Maximum number of orders to return
            status: Filter by order status (optional)

        Returns:
            List of Order instances
        """
        query = select(Order).where(Order.bot_id == uuid.UUID(bot_id))

        if status:
            query = query.where(Order.status == status)

        query = query.order_by(Order.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_active_orders(self, bot_id: str) -> List[Order]:
        """
        Get active (non-completed) orders for a bot.

        Args:
            bot_id: Bot UUID

        Returns:
            List of active Order instances
        """
        result = await self.db.execute(
            select(Order)
            .where(Order.bot_id == uuid.UUID(bot_id))
            .where(Order.status.in_([OrderStatus.PENDING, OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]))
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()

    async def cancel_order(
        self,
        order_id: uuid.UUID,
        error_message: Optional[str] = None
    ) -> Order:
        """
        Mark order as cancelled in database.

        Args:
            order_id: Order UUID
            error_message: Optional cancellation reason

        Returns:
            Updated Order instance
        """
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one()

        order.status = OrderStatus.CANCELLED
        order.completed_at = datetime.now()

        if error_message:
            order.error_message = error_message

        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def mark_order_failed(
        self,
        order_id: uuid.UUID,
        error_message: str,
        retry_count: Optional[int] = None
    ) -> Order:
        """
        Mark order as failed in database.

        Args:
            order_id: Order UUID
            error_message: Failure reason
            retry_count: Number of retry attempts

        Returns:
            Updated Order instance
        """
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one()

        order.status = OrderStatus.FAILED
        order.error_message = error_message
        order.completed_at = datetime.now()

        if retry_count is not None:
            order.retry_count = retry_count

        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def get_order_statistics(self, bot_id: str) -> Dict[str, Any]:
        """
        Get order statistics for a bot.

        Args:
            bot_id: Bot UUID

        Returns:
            Dictionary with order statistics
        """
        orders = await self.get_bot_orders(bot_id, limit=1000)

        total_orders = len(orders)
        filled_orders = len([o for o in orders if o.status == OrderStatus.FILLED])
        cancelled_orders = len([o for o in orders if o.status == OrderStatus.CANCELLED])
        failed_orders = len([o for o in orders if o.status == OrderStatus.FAILED])
        active_orders = len([o for o in orders if o.status in [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]])

        total_commission = sum(o.commission for o in orders if o.commission)
        total_volume = sum(o.quote_quantity for o in orders if o.quote_quantity)

        return {
            "total_orders": total_orders,
            "filled_orders": filled_orders,
            "cancelled_orders": cancelled_orders,
            "failed_orders": failed_orders,
            "active_orders": active_orders,
            "fill_rate": (filled_orders / total_orders * 100) if total_orders > 0 else 0,
            "total_commission": total_commission,
            "total_volume": total_volume
        }
