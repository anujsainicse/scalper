"""
Order Service - Centralized order placement logic

This service provides a unified interface for placing orders, whether for:
- Bot initial orders (when starting)
- Opposite orders (when an order fills)
- Infinite loop continuation orders
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from typing import Optional

from app.models.bot import Bot, BotStatus
from app.models.order import Order, OrderStatus, OrderType as DBOrderType
from app.models.bot import OrderSide as BotOrderSide, Exchange as BotExchange
from app.exchanges.base import OrderRequest, OrderSide, OrderType
from app.exchanges import ExchangeFactory

logger = logging.getLogger(__name__)


def get_exchange_for_bot(bot: Bot):
    """Get the appropriate exchange adapter for a bot"""
    exchange_map = {
        BotExchange.COINDCX_F: "coindcx",
        BotExchange.BINANCE: "binance"
    }

    exchange_name = exchange_map.get(bot.exchange)
    if not exchange_name:
        raise ValueError(f"Unsupported exchange: {bot.exchange}")

    return ExchangeFactory.create_sync(exchange_name)


async def place_order_for_bot(
    bot: Bot,
    side: BotOrderSide,
    price: float,
    db: AsyncSession,
    paired_order_id: Optional[str] = None,
    leverage: Optional[int] = None
) -> Order:
    """
    Place an order for a bot on the exchange and create database record.

    Args:
        bot: The bot placing the order
        side: BUY or SELL
        price: Order price
        db: Database session
        paired_order_id: Optional ID of the paired opposite order
        leverage: Optional leverage override (uses bot.leverage if not provided)

    Returns:
        The created Order database record

    Raises:
        Exception: If order placement fails
    """
    try:
        # Get exchange adapter
        exchange = get_exchange_for_bot(bot)

        # Determine leverage
        if leverage is None:
            # Use the bot's configured leverage or default to 3x
            leverage = bot.leverage if bot.leverage else 3
            logger.info(f"Using bot's configured leverage {leverage}x")

        # Convert side to exchange enum
        exchange_side = OrderSide.BUY if side == BotOrderSide.BUY else OrderSide.SELL

        # Create order request
        order_request = OrderRequest(
            symbol=bot.ticker,  # e.g., "ETH/USDT"
            side=exchange_side,
            order_type=OrderType.LIMIT,
            quantity=float(bot.quantity),
            price=float(price),
            leverage=leverage,
            time_in_force="GTC"
        )

        logger.info(
            f"Placing {exchange_side.value} order for bot {bot.id}: "
            f"{bot.ticker} @ ${price} with {leverage}x leverage"
        )

        # Place order on exchange
        order_response = await exchange.place_order(order_request)

        # Create order record in database
        db_order = Order(
            bot_id=bot.id,
            exchange_order_id=order_response.order_id,
            symbol=bot.ticker,
            side=side,
            order_type=DBOrderType.LIMIT,
            quantity=bot.quantity,
            price=price,
            status=OrderStatus.PENDING,
            filled_quantity=float(order_response.filled_quantity),
            filled_price=float(order_response.average_price) if order_response.average_price else None,
            commission=0.0,
            paired_order_id=paired_order_id
        )
        db.add(db_order)
        await db.flush()  # Get the ID without committing

        logger.info(
            f"Order {db_order.id} created successfully. "
            f"Exchange order ID: {order_response.order_id}"
        )

        return db_order

    except Exception as e:
        logger.error(f"Failed to place order for bot {bot.id}: {e}")
        raise


async def get_order_by_exchange_id(exchange_order_id: str, db: AsyncSession) -> Optional[Order]:
    """
    Get an order by its exchange order ID

    Args:
        exchange_order_id: The order ID from the exchange
        db: Database session

    Returns:
        Order if found, None otherwise
    """
    result = await db.execute(
        select(Order).where(Order.exchange_order_id == exchange_order_id)
    )
    return result.scalar_one_or_none()


async def update_order_status(
    order: Order,
    new_status: OrderStatus,
    filled_quantity: Optional[float] = None,
    filled_price: Optional[float] = None,
    db: AsyncSession = None
) -> Order:
    """
    Update an order's status and fill details

    Args:
        order: The order to update
        new_status: New status
        filled_quantity: Optional filled quantity
        filled_price: Optional filled price
        db: Database session (optional, for immediate commit)

    Returns:
        Updated order
    """
    order.status = new_status

    if filled_quantity is not None:
        order.filled_quantity = filled_quantity

    if filled_price is not None:
        order.filled_price = filled_price

    if db:
        await db.flush()

    logger.info(
        f"Order {order.id} status updated: {new_status.value}. "
        f"Filled: {order.filled_quantity}/{order.quantity}"
    )

    return order
