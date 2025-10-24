from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID
import logging

from app.db.session import get_db
from app.models.bot import Bot, ActivityLog, BotStatus, OrderSide as BotOrderSide
from app.models.order import Order as OrderModel, OrderStatus as DBOrderStatus, OrderType as DBOrderType
from app.schemas.bot import (
    BotCreate,
    BotUpdate,
    BotResponse,
    BotStatusUpdate,
    BotStatistics,
    ActivityLogResponse,
    ActivityLogCreate
)
from app.schemas.order import OrderResponse
from app.services.telegram import telegram_service
from app.services.order_service import place_order_for_bot, get_exchange_for_bot as get_exchange_adapter
from app.services.websocket_manager import ws_manager
from app.exchanges import ExchangeFactory, OrderRequest, OrderSide, OrderType, BaseExchange

router = APIRouter()
logger = logging.getLogger(__name__)


def get_exchange_for_bot(bot: Bot) -> BaseExchange:
    """
    Get exchange adapter for a bot

    Args:
        bot: Bot instance

    Returns:
        Initialized exchange adapter

    Raises:
        ValueError: If exchange is not supported or credentials missing
    """
    # Map bot exchange to exchange name for factory
    exchange_map = {
        "CoinDCX F": "coindcx",
        "Binance": "binance",
    }

    exchange_name = exchange_map.get(bot.exchange.value)
    if not exchange_name:
        raise ValueError(f"Exchange {bot.exchange.value} not supported")

    # Create exchange adapter
    try:
        exchange = ExchangeFactory.create_sync(exchange_name)
        return exchange
    except Exception as e:
        logger.error(f"Failed to create exchange adapter for {exchange_name}: {e}")
        raise ValueError(f"Failed to initialize exchange: {str(e)}")


@router.get("/", response_model=List[BotResponse])
async def get_bots(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all bots with optional filtering
    """
    query = select(Bot)

    if status:
        query = query.where(Bot.status == status)

    query = query.offset(skip).limit(limit).order_by(Bot.created_at.desc())

    result = await db.execute(query)
    bots = result.scalars().all()

    return bots


@router.post("/", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
async def create_bot(
    bot_data: BotCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new bot and place initial order on exchange
    """
    # Create bot with ACTIVE status
    bot = Bot(
        ticker=bot_data.ticker,
        exchange=bot_data.exchange,
        first_order=bot_data.first_order,
        quantity=bot_data.quantity,
        buy_price=bot_data.buy_price,
        sell_price=bot_data.sell_price,
        trailing_percent=bot_data.trailing_percent,
        leverage=bot_data.leverage if bot_data.leverage else 3,
        infinite_loop=bot_data.infinite_loop,
        status=BotStatus.ACTIVE,
    )

    db.add(bot)
    await db.flush()

    try:
        # Get exchange adapter
        exchange = get_exchange_for_bot(bot)

        # Use the leverage from bot configuration
        leverage = bot.leverage if bot.leverage else 3
        logger.info(f"Using leverage {leverage}x from bot configuration for {bot.ticker}")

        # Determine order side and price based on first_order
        order_side = OrderSide.BUY if bot.first_order == BotOrderSide.BUY else OrderSide.SELL
        order_price = bot.buy_price if bot.first_order == BotOrderSide.BUY else bot.sell_price

        # Create order request
        order_request = OrderRequest(
            symbol=bot.ticker,
            side=order_side,
            order_type=OrderType.LIMIT,
            quantity=float(bot.quantity),
            price=float(order_price),
            leverage=leverage,  # Use existing position leverage or default 3x
            time_in_force="GTC"
        )

        logger.info(
            f"Placing {order_side.value} order for new bot {bot.id}: {bot.ticker} @ {order_price} "
            f"with {leverage}x leverage"
        )

        # Place order on exchange
        order_response = await exchange.place_order(order_request)

        # Create order record in database
        db_order = OrderModel(
            bot_id=bot.id,
            exchange_order_id=order_response.order_id,
            symbol=bot.ticker,
            side=bot.first_order,
            order_type=DBOrderType.LIMIT,
            quantity=bot.quantity,
            price=order_price,
            status=DBOrderStatus.PENDING,
            filled_quantity=float(order_response.filled_quantity),
            filled_price=float(order_response.average_price) if order_response.average_price else None,
            commission=0.0
        )
        db.add(db_order)

        # Create activity log
        log = ActivityLog(
            bot_id=bot.id,
            level="SUCCESS",
            message=f"Bot started and {order_side.value} order placed at ${order_price}"
        )
        db.add(log)

        await db.commit()
        await db.refresh(bot)

        # Broadcast bot creation via WebSocket
        await ws_manager.broadcast_bot_created({
            "id": str(bot.id),
            "ticker": bot.ticker,
            "exchange": bot.exchange.value,
            "status": bot.status.value,
            "quantity": float(bot.quantity),
            "buy_price": float(bot.buy_price),
            "sell_price": float(bot.sell_price),
        })

        logger.info(f"Bot {bot.id} started successfully with order {order_response.order_id}")
        return bot

    except ValueError as ve:
        # Exchange configuration error
        logger.error(f"Exchange configuration error for new bot: {ve}")

        bot.status = BotStatus.ERROR

        log = ActivityLog(
            bot_id=bot.id,
            level="ERROR",
            message=f"Failed to start bot: {str(ve)}"
        )
        db.add(log)

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Exchange configuration error: {str(ve)}"
        )

    except Exception as e:
        # Order placement failed
        logger.error(f"Failed to place order for new bot: {e}")

        bot.status = BotStatus.ERROR

        log = ActivityLog(
            bot_id=bot.id,
            level="ERROR",
            message=f"Failed to place order: {str(e)}"
        )
        db.add(log)

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place order on exchange: {str(e)}"
        )


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific bot by ID
    """
    result = await db.execute(select(Bot).where(Bot.id == bot_id))
    bot = result.scalar_one_or_none()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    return bot


@router.put("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: UUID,
    bot_data: BotUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a bot's configuration and manage exchange orders

    If bot is ACTIVE:
    - Cancels all pending orders on exchange
    - Updates bot configuration
    - Places new orders with updated parameters

    If bot is STOPPED:
    - Only updates configuration in database
    """
    logger.info(f"[UPDATE-BOT] Received update request for bot_id: {bot_id}")

    result = await db.execute(select(Bot).where(Bot.id == bot_id))
    bot = result.scalar_one_or_none()

    if not bot:
        logger.warning(f"[UPDATE-BOT] Bot {bot_id} not found")
        raise HTTPException(status_code=404, detail="Bot not found")

    is_active = bot.status == BotStatus.ACTIVE
    logger.info(f"[UPDATE-BOT] Bot status: {bot.status.value}")

    # Store old values for comparison
    old_buy_price = bot.buy_price
    old_sell_price = bot.sell_price
    old_quantity = bot.quantity
    old_first_order = bot.first_order

    # Update bot fields
    update_data = bot_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bot, field, value)

    logger.info(f"[UPDATE-BOT] Bot configuration updated in database")

    # If bot is ACTIVE, manage orders on exchange
    if is_active:
        logger.info(f"[UPDATE-BOT] Bot is ACTIVE, managing exchange orders...")

        try:
            # Get exchange adapter
            exchange = get_exchange_for_bot(bot)

            # Get all pending orders for this bot
            orders_result = await db.execute(
                select(OrderModel).where(
                    OrderModel.bot_id == bot_id,
                    OrderModel.status.in_([DBOrderStatus.PENDING, DBOrderStatus.PARTIALLY_FILLED])
                )
            )
            pending_orders = orders_result.scalars().all()

            cancelled_count = 0

            # Cancel all pending orders
            # CRITICAL: Set cancellation_reason BEFORE calling exchange API to avoid race condition
            for order in pending_orders:
                try:
                    logger.info(f"[UPDATE-BOT] Marking order {order.exchange_order_id} for UPDATE cancellation")
                    # Set cancellation reason FIRST (before exchange call)
                    order.cancellation_reason = "UPDATE"
                    order.status = DBOrderStatus.CANCELLED
                    # Commit to database BEFORE calling exchange API
                    await db.flush()
                    logger.info(f"[UPDATE-BOT] Cancellation reason committed to database")

                    # Now cancel on exchange (this will trigger WebSocket event)
                    logger.info(f"[UPDATE-BOT] Cancelling order {order.exchange_order_id} on exchange")
                    await exchange.cancel_order(order.exchange_order_id, bot.ticker)
                    cancelled_count += 1
                    logger.info(f"[UPDATE-BOT] Order {order.exchange_order_id} cancelled successfully")
                except Exception as cancel_error:
                    logger.error(f"[UPDATE-BOT] Failed to cancel order {order.exchange_order_id}: {cancel_error}")
                    # Continue with other orders even if one fails
                    pass

            if cancelled_count > 0:
                log = ActivityLog(
                    bot_id=bot.id,
                    level="INFO",
                    message=f"{cancelled_count} pending order(s) cancelled"
                )
                db.add(log)
                logger.info(f"[UPDATE-BOT] Cancelled {cancelled_count} order(s)")

            # Place new order with updated parameters
            # Determine order side based on last filled order (opposite of last fill)
            last_filled_query = select(OrderModel).where(
                OrderModel.bot_id == bot_id,
                OrderModel.status == DBOrderStatus.FILLED
            ).order_by(OrderModel.created_at.desc()).limit(1)

            last_filled_result = await db.execute(last_filled_query)
            last_filled_order = last_filled_result.scalar_one_or_none()

            if last_filled_order:
                # Place opposite of what was last filled
                if last_filled_order.side == BotOrderSide.BUY:
                    order_side_enum = OrderSide.SELL
                    bot_order_side = BotOrderSide.SELL
                    order_price = bot.sell_price
                    logger.info(f"[UPDATE-BOT] Last filled was BUY, placing SELL order")
                else:
                    order_side_enum = OrderSide.BUY
                    bot_order_side = BotOrderSide.BUY
                    order_price = bot.buy_price
                    logger.info(f"[UPDATE-BOT] Last filled was SELL, placing BUY order")
            else:
                # No filled orders yet - use first_order as fallback
                order_side_enum = OrderSide.BUY if bot.first_order == BotOrderSide.BUY else OrderSide.SELL
                bot_order_side = bot.first_order
                order_price = bot.buy_price if bot.first_order == BotOrderSide.BUY else bot.sell_price
                logger.info(f"[UPDATE-BOT] No filled orders, using first_order: {bot.first_order.value}")

            leverage = bot.leverage if bot.leverage else 3

            # Create order request
            order_request = OrderRequest(
                symbol=bot.ticker,
                side=order_side_enum,
                order_type=OrderType.LIMIT,
                quantity=float(bot.quantity),
                price=float(order_price),
                leverage=leverage,
                time_in_force="GTC"
            )

            logger.info(
                f"[UPDATE-BOT] Placing new {order_side_enum.value} order: "
                f"{bot.ticker} @ ${order_price} qty={bot.quantity}"
            )

            # Place order on exchange
            order_response = await exchange.place_order(order_request)

            # Create order record in database
            new_order = OrderModel(
                bot_id=bot.id,
                exchange_order_id=order_response.order_id,
                symbol=bot.ticker,
                side=bot_order_side,
                order_type=DBOrderType.LIMIT,
                quantity=bot.quantity,
                price=order_price,
                status=DBOrderStatus.PENDING,
                filled_quantity=float(order_response.filled_quantity),
                filled_price=float(order_response.average_price) if order_response.average_price else None,
                commission=0.0
            )
            db.add(new_order)

            log = ActivityLog(
                bot_id=bot.id,
                level="SUCCESS",
                message=f"New {order_side_enum.value} order placed at ${order_price}"
            )
            db.add(log)

            logger.info(f"[UPDATE-BOT] New order placed successfully: {order_response.order_id}")

        except Exception as e:
            logger.error(f"[UPDATE-BOT] Error managing exchange orders: {e}")
            bot.status = BotStatus.ERROR

            log = ActivityLog(
                bot_id=bot.id,
                level="ERROR",
                message=f"Failed to update orders on exchange: {str(e)}"
            )
            db.add(log)

            await db.commit()
            await db.refresh(bot)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update orders on exchange: {str(e)}"
            )
    else:
        # Bot is STOPPED, just update configuration
        logger.info(f"[UPDATE-BOT] Bot is STOPPED, only updating configuration")
        log = ActivityLog(
            bot_id=bot.id,
            level="INFO",
            message=f"Bot configuration updated (bot is {bot.status.value})"
        )
        db.add(log)

    await db.commit()
    await db.refresh(bot)

    # Broadcast bot update via WebSocket
    await ws_manager.broadcast_bot_update(str(bot.id), {
        "ticker": bot.ticker,
        "exchange": bot.exchange.value,
        "status": bot.status.value,
        "quantity": float(bot.quantity),
        "buy_price": float(bot.buy_price),
        "sell_price": float(bot.sell_price),
        "pnl": float(bot.pnl) if bot.pnl else 0.0,
        "total_trades": bot.total_trades,
    })

    logger.info(f"[UPDATE-BOT] Bot {bot_id} updated successfully")
    return bot


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(
    bot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a bot and cancel all its open orders
    """
    logger.info(f"[DELETE-BOT] Received delete request for bot_id: {bot_id}")

    result = await db.execute(select(Bot).where(Bot.id == bot_id))
    bot = result.scalar_one_or_none()

    if not bot:
        logger.warning(f"[DELETE-BOT] Bot {bot_id} not found")
        raise HTTPException(status_code=404, detail="Bot not found")

    logger.info(f"[DELETE-BOT] Found bot: {bot.ticker} on {bot.exchange.value}")

    # Store bot info before deleting
    ticker = bot.ticker
    exchange = bot.exchange.value

    # Cancel all open orders for this bot
    cancelled_count = 0
    try:
        # Get all pending orders for this bot
        logger.info(f"[DELETE-BOT] Checking for pending orders...")
        orders_result = await db.execute(
            select(OrderModel).where(
                OrderModel.bot_id == bot_id,
                OrderModel.status == DBOrderStatus.PENDING
            )
        )
        open_orders = orders_result.scalars().all()

        if open_orders:
            logger.info(f"[DELETE-BOT] Cancelling {len(open_orders)} open orders for bot {bot_id}")

            # Get exchange adapter
            exchange_adapter = get_exchange_for_bot(bot)

            # Cancel each order
            for order in open_orders:
                try:
                    logger.info(f"[DELETE-BOT] Attempting to cancel order {order.exchange_order_id}")

                    # Set cancellation reason FIRST (before exchange call) to avoid race condition
                    order.cancellation_reason = "DELETE"
                    order.status = DBOrderStatus.CANCELLED
                    # Commit to database BEFORE calling exchange API
                    await db.flush()
                    logger.info(f"[DELETE-BOT] Cancellation reason committed for order {order.exchange_order_id}")

                    # Cancel on exchange (this will trigger WebSocket event)
                    success = await exchange_adapter.cancel_order(
                        order_id=order.exchange_order_id,
                        symbol=order.symbol
                    )

                    if success:
                        cancelled_count += 1
                        logger.info(f"[DELETE-BOT] Successfully cancelled order {order.exchange_order_id}")
                    else:
                        # Order might already be cancelled on exchange
                        logger.warning(f"[DELETE-BOT] Exchange returned false for order {order.exchange_order_id}")

                except Exception as e:
                    # Order might have been manually cancelled on exchange
                    logger.warning(f"[DELETE-BOT] Could not cancel order {order.exchange_order_id}: {e}")
                    logger.info(f"[DELETE-BOT] Order already marked as cancelled in database")

            await db.flush()

    except Exception as e:
        logger.error(f"[DELETE-BOT] Error during order cancellation for bot {bot_id}: {e}")
    else:
        logger.info(f"[DELETE-BOT] No pending orders found")

    # Create activity log before deleting
    logger.info(f"[DELETE-BOT] Creating activity log...")
    cancel_msg = f" ({cancelled_count} orders cancelled)" if cancelled_count > 0 else ""
    log = ActivityLog(
        bot_id=bot.id,
        level="WARNING",
        message=f"Bot deleted for {bot.ticker}{cancel_msg}"
    )
    db.add(log)

    logger.info(f"[DELETE-BOT] Deleting bot from database...")
    await db.delete(bot)
    await db.commit()
    logger.info(f"[DELETE-BOT] Bot deleted successfully from database")

    # Broadcast bot deletion via WebSocket
    await ws_manager.broadcast_bot_deleted(str(bot_id))

    logger.info(f"[DELETE-BOT] Delete operation completed successfully")

    return None


@router.post("/{bot_id}/start", response_model=BotResponse)
async def start_bot(
    bot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Start a bot and place initial order on exchange
    """
    result = await db.execute(select(Bot).where(Bot.id == bot_id))
    bot = result.scalar_one_or_none()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    try:
        # Determine order side and price based on first_order
        order_side = bot.first_order
        order_price = bot.buy_price if bot.first_order == BotOrderSide.BUY else bot.sell_price

        # Use the new centralized order service
        db_order = await place_order_for_bot(
            bot=bot,
            side=order_side,
            price=order_price,
            db=db
        )

        # Set bot status to ACTIVE
        bot.status = BotStatus.ACTIVE

        # Create activity log
        log = ActivityLog(
            bot_id=bot.id,
            level="SUCCESS",
            message=f"Bot started and {order_side.value} order placed at ${order_price}"
        )
        db.add(log)

        await db.commit()
        await db.refresh(bot)

        logger.info(f"Bot {bot.id} started successfully with order {db_order.exchange_order_id}")
        return bot

    except ValueError as ve:
        # Exchange configuration error
        logger.error(f"Exchange configuration error for bot {bot.id}: {ve}")

        bot.status = BotStatus.ERROR

        log = ActivityLog(
            bot_id=bot.id,
            level="ERROR",
            message=f"Failed to start bot: {str(ve)}"
        )
        db.add(log)

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Exchange configuration error: {str(ve)}"
        )

    except Exception as e:
        # Order placement failed
        logger.error(f"Failed to place order for bot {bot.id}: {e}")

        bot.status = BotStatus.ERROR

        log = ActivityLog(
            bot_id=bot.id,
            level="ERROR",
            message=f"Failed to place order: {str(e)}"
        )
        db.add(log)

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place order on exchange: {str(e)}"
        )


@router.post("/{bot_id}/stop", response_model=BotResponse)
async def stop_bot(
    bot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Stop a bot and cancel all pending orders
    """
    result = await db.execute(select(Bot).where(Bot.id == bot_id))
    bot = result.scalar_one_or_none()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Get all pending orders for this bot
    pending_orders_query = select(OrderModel).where(
        OrderModel.bot_id == bot_id,
        OrderModel.status == DBOrderStatus.PENDING
    )
    pending_orders_result = await db.execute(pending_orders_query)
    pending_orders = pending_orders_result.scalars().all()

    cancelled_count = 0
    failed_cancellations = []

    # Cancel orders on exchange if there are any pending orders
    if pending_orders:
        try:
            # Get exchange adapter
            exchange = get_exchange_for_bot(bot)

            for order in pending_orders:
                try:
                    # Set cancellation reason FIRST (before exchange call) to avoid race condition
                    order.cancellation_reason = "STOP"
                    order.status = DBOrderStatus.CANCELLED
                    # Commit to database BEFORE calling exchange API
                    await db.flush()
                    logger.info(f"Cancellation reason committed for order {order.exchange_order_id}")

                    # Cancel order on exchange (this will trigger WebSocket event)
                    success = await exchange.cancel_order(order.exchange_order_id, order.symbol)

                    if success:
                        cancelled_count += 1
                        logger.info(f"Cancelled order {order.exchange_order_id} for bot {bot.id}")
                    else:
                        failed_cancellations.append(order.exchange_order_id)
                        logger.warning(f"Failed to cancel order {order.exchange_order_id}")

                except Exception as e:
                    failed_cancellations.append(order.exchange_order_id)
                    logger.error(f"Error cancelling order {order.exchange_order_id}: {e}")

        except ValueError as ve:
            # Exchange configuration error - still stop bot but log the error
            logger.error(f"Exchange configuration error while stopping bot {bot.id}: {ve}")
            log = ActivityLog(
                bot_id=bot.id,
                level="WARNING",
                message=f"Could not cancel orders: {str(ve)}"
            )
            db.add(log)

    # Set bot status to STOPPED
    bot.status = BotStatus.STOPPED

    # Create activity log
    if pending_orders:
        if cancelled_count > 0:
            log_message = f"Bot stopped and {cancelled_count} pending order(s) cancelled"
            if failed_cancellations:
                log_message += f" ({len(failed_cancellations)} failed)"
        else:
            log_message = f"Bot stopped ({len(pending_orders)} order(s) could not be cancelled)"
    else:
        log_message = f"Bot stopped (no pending orders)"

    log = ActivityLog(
        bot_id=bot.id,
        level="WARNING",
        message=log_message
    )
    db.add(log)

    await db.commit()
    await db.refresh(bot)

    # Send Telegram notification
    telegram_msg = (
        f"*Bot Stopped*\n\n"
        f"Ticker: {bot.ticker}\n"
        f"Exchange: {bot.exchange.value}\n"
    )

    if pending_orders:
        telegram_msg += f"Orders Cancelled: {cancelled_count}/{len(pending_orders)}\n"

    telegram_msg += f"Status: STOPPED"

    await telegram_service.send_notification(
        db=db,
        message=telegram_msg,
        level="WARNING"
    )

    logger.info(f"Bot {bot.id} stopped. Cancelled {cancelled_count}/{len(pending_orders)} orders")

    return bot


@router.post("/{bot_id}/toggle", response_model=BotResponse)
async def toggle_bot(
    bot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle bot status (ACTIVE <-> STOPPED)
    """
    result = await db.execute(select(Bot).where(Bot.id == bot_id))
    bot = result.scalar_one_or_none()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Toggle status
    new_status = BotStatus.STOPPED if bot.status == BotStatus.ACTIVE else BotStatus.ACTIVE
    bot.status = new_status

    log_level = "SUCCESS" if new_status == BotStatus.ACTIVE else "WARNING"
    log = ActivityLog(
        bot_id=bot.id,
        level=log_level,
        message=f"Bot {new_status.value.lower()} for {bot.ticker}"
    )
    db.add(log)

    await db.commit()
    await db.refresh(bot)

    # Broadcast bot update via WebSocket
    await ws_manager.broadcast_bot_update(str(bot.id), {
        "status": bot.status.value,
        "ticker": bot.ticker,
        "exchange": bot.exchange.value,
    })

    return bot


@router.post("/stop-all", status_code=status.HTTP_200_OK)
async def stop_all_bots(
    db: AsyncSession = Depends(get_db)
):
    """
    Stop all active bots
    """
    result = await db.execute(select(Bot).where(Bot.status == BotStatus.ACTIVE))
    bots = result.scalars().all()

    for bot in bots:
        bot.status = BotStatus.STOPPED

    # Create activity log
    log = ActivityLog(
        level="ERROR",
        message="Emergency stop - All bots stopped"
    )
    db.add(log)

    await db.commit()

    return {"message": f"Stopped {len(bots)} bots", "count": len(bots)}


@router.get("/statistics/summary", response_model=BotStatistics)
async def get_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    Get bot statistics
    """
    # Total bots
    total_result = await db.execute(select(func.count(Bot.id)))
    total_bots = total_result.scalar()

    # Active bots
    active_result = await db.execute(
        select(func.count(Bot.id)).where(Bot.status == BotStatus.ACTIVE)
    )
    active_bots = active_result.scalar()

    # Stopped bots
    stopped_bots = total_bots - active_bots

    # Total PnL
    pnl_result = await db.execute(select(func.sum(Bot.pnl)))
    total_pnl = pnl_result.scalar() or 0.0

    # Total trades
    trades_result = await db.execute(select(func.sum(Bot.total_trades)))
    total_trades = trades_result.scalar() or 0

    return {
        "total_bots": total_bots,
        "active_bots": active_bots,
        "stopped_bots": stopped_bots,
        "total_pnl": total_pnl,
        "total_trades": total_trades
    }


@router.get("/{bot_id}/orders", response_model=List[OrderResponse])
async def get_bot_orders(
    bot_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all orders for a specific bot
    """
    # Verify bot exists
    bot_result = await db.execute(select(Bot).where(Bot.id == bot_id))
    bot = bot_result.scalar_one_or_none()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Get orders for this bot
    query = select(Order).where(Order.bot_id == bot_id).offset(skip).limit(limit).order_by(Order.created_at.desc())
    result = await db.execute(query)
    orders = result.scalars().all()

    return orders
