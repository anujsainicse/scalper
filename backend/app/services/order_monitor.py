"""
Order Monitor Service - Handles order fill detection and opposite order placement

This service monitors order status changes (via WebSocket events) and:
1. Detects when orders are completely filled
2. Places opposite orders automatically
3. Links order pairs (buy-sell cycles)
4. Calculates PnL for completed cycles
5. Updates bot metrics (total_trades, pnl, last_fill_time)
6. Handles infinite loop continuation
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging
import asyncio
from typing import Optional, Tuple

from app.models.bot import Bot, BotStatus
from app.models.order import Order, OrderStatus
from app.models.bot import OrderSide as BotOrderSide
from app.models.bot import ActivityLog
from app.services.order_service import (
    place_order_for_bot,
    get_order_by_exchange_id,
    update_order_status
)
from app.services.telegram import telegram_service

logger = logging.getLogger(__name__)

# Lock to prevent duplicate order processing
_processing_locks = {}
_locks_lock = asyncio.Lock()


async def process_order_fill(
    exchange_order_id: str,
    filled_quantity: float,
    total_quantity: float,
    filled_price: Optional[float],
    db: AsyncSession
) -> bool:
    """
    Process an order fill event from WebSocket

    Args:
        exchange_order_id: Exchange order ID
        filled_quantity: Amount filled
        total_quantity: Total order quantity
        filled_price: Price at which order filled
        db: Database session

    Returns:
        True if processing successful, False otherwise
    """
    # Get or create a lock for this specific order
    async with _locks_lock:
        if exchange_order_id not in _processing_locks:
            _processing_locks[exchange_order_id] = asyncio.Lock()
        order_lock = _processing_locks[exchange_order_id]

    # Acquire the lock for this order to prevent duplicate processing
    async with order_lock:
        try:
            # Check if order is completely filled
            if filled_quantity < total_quantity:
                logger.info(
                    f"Order {exchange_order_id} partially filled: "
                    f"{filled_quantity}/{total_quantity}. Waiting for complete fill."
                )
                return False

            # Get order from database
            order = await get_order_by_exchange_id(exchange_order_id, db)
            if not order:
                logger.warning(f"Order {exchange_order_id} not found in database")
                return False

            # Check if order already processed
            if order.status == OrderStatus.FILLED:
                logger.info(f"Order {order.id} already marked as FILLED. Skipping duplicate processing.")
                return False

            # Update order status to FILLED
            await update_order_status(
                order,
                OrderStatus.FILLED,
                filled_quantity=filled_quantity,
                filled_price=filled_price,
                db=db
            )

            # Get the bot
            result = await db.execute(select(Bot).where(Bot.id == order.bot_id))
            bot = result.scalar_one_or_none()
            if not bot:
                logger.error(f"Bot {order.bot_id} not found for order {order.id}")
                return False

            # Check if bot is still active
            if bot.status != BotStatus.ACTIVE:
                logger.info(f"Bot {bot.id} is {bot.status.value}. Not placing opposite order.")
                return False

            # Update bot's last fill details
            bot.last_fill_time = datetime.utcnow()
            bot.last_fill_side = order.side
            bot.last_fill_price = float(filled_price if filled_price else order.price)

            # Log the fill
            log = ActivityLog(
                bot_id=bot.id,
                level="SUCCESS",
                message=f"{order.side.value} order filled at ${order.filled_price or order.price}"
            )
            db.add(log)

            # Place opposite order
            opposite_order = await place_opposite_order(order, bot, db)

            if opposite_order:
                logger.info(
                    f"Successfully placed opposite order {opposite_order.id} "
                    f"for filled order {order.id}"
                )

                # Link the orders
                order.paired_order_id = opposite_order.id
                opposite_order.paired_order_id = order.id

                # Log opposite order placement
                log = ActivityLog(
                    bot_id=bot.id,
                    level="INFO",
                    message=f"{opposite_order.side.value} order placed at ${opposite_order.price} (opposite of filled order)"
                )
                db.add(log)

                # Send Telegram notification
                await telegram_service.send_notification(
                    db=db,
                    message=f"*Order Filled \u2192 Opposite Order Placed*\n\n"
                            f"Bot: {bot.ticker}\n"
                            f"Filled: {order.side.value} @ ${order.filled_price or order.price}\n"
                            f"Placed: {opposite_order.side.value} @ ${opposite_order.price}\n"
                            f"Quantity: {bot.quantity}",
                    level="SUCCESS"
                )

            await db.commit()

            # Check if this completes a cycle (sell order of a buy-sell pair)
            if order.side == BotOrderSide.SELL and order.paired_order_id:
                await complete_trading_cycle(order, bot, db)

            return True

        except Exception as e:
            logger.error(f"Error processing order fill for {exchange_order_id}: {e}")
            await db.rollback()
            return False


async def place_opposite_order(
    filled_order: Order,
    bot: Bot,
    db: AsyncSession
) -> Optional[Order]:
    """
    Place the opposite order after an order fills

    Args:
        filled_order: The order that just filled
        bot: The bot that owns the order
        db: Database session

    Returns:
        The newly created opposite order, or None if failed
    """
    try:
        # Determine opposite side
        if filled_order.side == BotOrderSide.BUY:
            opposite_side = BotOrderSide.SELL
            opposite_price = bot.sell_price
        else:
            opposite_side = BotOrderSide.BUY
            opposite_price = bot.buy_price

        # Place the opposite order
        opposite_order = await place_order_for_bot(
            bot=bot,
            side=opposite_side,
            price=opposite_price,
            db=db,
            paired_order_id=filled_order.id  # Link to filled order
        )

        return opposite_order

    except Exception as e:
        logger.error(
            f"Failed to place opposite order for order {filled_order.id}: {e}"
        )
        # Log error but don't raise - we don't want to block the main flow
        log = ActivityLog(
            bot_id=bot.id,
            level="ERROR",
            message=f"Failed to place opposite {opposite_side.value} order: {str(e)}"
        )
        db.add(log)
        return None


async def complete_trading_cycle(
    sell_order: Order,
    bot: Bot,
    db: AsyncSession
) -> None:
    """
    Complete a trading cycle when a sell order fills

    This calculates PnL, updates bot metrics, and optionally starts
    a new cycle if infinite loop is enabled.

    Args:
        sell_order: The sell order that just filled
        bot: The bot that owns the order
        db: Database session
    """
    try:
        # Get the paired buy order
        if not sell_order.paired_order_id:
            logger.warning(f"Sell order {sell_order.id} has no paired buy order")
            return

        result = await db.execute(
            select(Order).where(Order.id == sell_order.paired_order_id)
        )
        buy_order = result.scalar_one_or_none()

        if not buy_order:
            logger.error(f"Paired buy order {sell_order.paired_order_id} not found")
            return

        # Calculate PnL
        pnl = await calculate_cycle_pnl(buy_order, sell_order)

        # Update bot metrics
        bot.total_trades += 1  # One complete cycle = one trade
        bot.pnl += pnl

        logger.info(
            f"Trading cycle completed for bot {bot.id}. "
            f"PnL: ${pnl:.2f}, Total PnL: ${bot.pnl:.2f}, "
            f"Total Trades: {bot.total_trades}"
        )

        # Log the cycle completion
        log = ActivityLog(
            bot_id=bot.id,
            level="SUCCESS",
            message=f"Trading cycle completed! PnL: ${pnl:.2f} | Total PnL: ${bot.pnl:.2f}"
        )
        db.add(log)

        # Send Telegram notification
        pnl_emoji = "\ud83d\udfe2" if pnl > 0 else "\ud83d\udd34" if pnl < 0 else "\u26ab"
        await telegram_service.send_notification(
            db=db,
            message=f"*Trading Cycle Completed* {pnl_emoji}\n\n"
                    f"Bot: {bot.ticker}\n"
                    f"Buy: ${buy_order.filled_price or buy_order.price}\n"
                    f"Sell: ${sell_order.filled_price or sell_order.price}\n"
                    f"Cycle PnL: ${pnl:.2f}\n"
                    f"Total PnL: ${bot.pnl:.2f}\n"
                    f"Total Trades: {bot.total_trades}",
            level="SUCCESS" if pnl >= 0 else "WARNING"
        )

        await db.commit()

    except Exception as e:
        logger.error(f"Error completing trading cycle for sell order {sell_order.id}: {e}")
        await db.rollback()


async def calculate_cycle_pnl(buy_order: Order, sell_order: Order) -> float:
    """
    Calculate profit/loss for a complete buy-sell cycle

    Args:
        buy_order: The buy order
        sell_order: The sell order

    Returns:
        PnL in quote currency (e.g., USDT)
    """
    # Use filled prices if available, otherwise use order prices
    buy_price = float(buy_order.filled_price or buy_order.price)
    sell_price = float(sell_order.filled_price or sell_order.price)
    quantity = float(sell_order.filled_quantity or sell_order.quantity)

    # Calculate gross PnL
    gross_pnl = (sell_price - buy_price) * quantity

    # Subtract commissions
    buy_commission = float(buy_order.commission or 0)
    sell_commission = float(sell_order.commission or 0)
    net_pnl = gross_pnl - buy_commission - sell_commission

    logger.info(
        f"PnL calculation: "
        f"(${sell_price} - ${buy_price}) * {quantity} - "
        f"${buy_commission + sell_commission} commission = ${net_pnl:.2f}"
    )

    return net_pnl
