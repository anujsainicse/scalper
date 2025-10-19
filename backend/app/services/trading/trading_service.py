"""
Trading Service

Orchestrates bot execution and integrates with exchange adapters.
"""

from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.bot import Bot, BotStatus, OrderSide as BotOrderSide
from app.models.order import Order, OrderStatus, OrderType, OrderSide
from app.models.credentials import ExchangeCredentials
from app.models.bot import ActivityLog
from app.exchanges import create_exchange_adapter
from app.utils.encryption import decrypt_api_key
from app.services.trading.order_manager import OrderManager


class TradingService:
    """
    Main service for orchestrating bot execution and trading operations.

    Responsibilities:
    - Start/stop bot execution
    - Get exchange credentials and create adapters
    - Execute buy/sell orders based on bot configuration
    - Track order lifecycle and update bot metrics
    - Handle infinite loop trading logic
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_manager = OrderManager(db)
        self._running_bots: Dict[str, asyncio.Task] = {}

    async def start_bot(self, bot_id: str) -> Dict[str, Any]:
        """
        Start bot execution.

        Args:
            bot_id: UUID of the bot to start

        Returns:
            dict with status and message
        """
        # Get bot from database
        result = await self.db.execute(select(Bot).where(Bot.id == bot_id))
        bot = result.scalar_one_or_none()

        if not bot:
            return {"success": False, "error": "Bot not found"}

        if bot.status == BotStatus.ACTIVE:
            return {"success": False, "error": "Bot is already running"}

        # Get exchange credentials
        credentials = await self._get_credentials(bot.exchange.value)
        if not credentials:
            await self._log_activity(
                bot_id=bot_id,
                level="ERROR",
                message=f"No credentials found for exchange {bot.exchange.value}"
            )
            return {"success": False, "error": f"No credentials configured for {bot.exchange.value}"}

        # Validate credentials
        if not credentials.is_validated:
            await self._log_activity(
                bot_id=bot_id,
                level="WARNING",
                message=f"Exchange credentials not validated for {bot.exchange.value}"
            )
            return {"success": False, "error": "Exchange credentials not validated"}

        # Update bot status to ACTIVE
        bot.status = BotStatus.ACTIVE
        await self.db.commit()

        # Log bot start
        await self._log_activity(
            bot_id=bot_id,
            level="SUCCESS",
            message=f"Bot started for {bot.ticker} on {bot.exchange.value}"
        )

        # Start bot execution in background
        task = asyncio.create_task(self._execute_bot(bot, credentials))
        self._running_bots[str(bot_id)] = task

        return {"success": True, "message": "Bot started successfully"}

    async def stop_bot(self, bot_id: str) -> Dict[str, Any]:
        """
        Stop bot execution.

        Args:
            bot_id: UUID of the bot to stop

        Returns:
            dict with status and message
        """
        # Get bot from database
        result = await self.db.execute(select(Bot).where(Bot.id == bot_id))
        bot = result.scalar_one_or_none()

        if not bot:
            return {"success": False, "error": "Bot not found"}

        if bot.status == BotStatus.STOPPED:
            return {"success": False, "error": "Bot is already stopped"}

        # Cancel running task if exists
        task_id = str(bot_id)
        if task_id in self._running_bots:
            task = self._running_bots[task_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self._running_bots[task_id]

        # Update bot status
        bot.status = BotStatus.STOPPED
        await self.db.commit()

        # Log bot stop
        await self._log_activity(
            bot_id=bot_id,
            level="INFO",
            message=f"Bot stopped for {bot.ticker}"
        )

        return {"success": True, "message": "Bot stopped successfully"}

    async def _execute_bot(self, bot: Bot, credentials: ExchangeCredentials):
        """
        Main bot execution loop.

        This method runs in the background and executes trading logic.
        For a scalper bot:
        1. Place first order (buy or sell based on configuration)
        2. Wait for fill
        3. Place opposite order
        4. Repeat if infinite_loop is enabled
        """
        try:
            # Create exchange adapter
            adapter = await self._create_adapter(credentials)

            # Validate credentials
            if not await adapter.validate_credentials():
                await self._handle_bot_error(bot, "Invalid exchange credentials")
                return

            # Log trading start
            await self._log_activity(
                bot_id=str(bot.id),
                level="INFO",
                message=f"Starting trading execution for {bot.ticker}"
            )

            # Main trading loop
            while bot.status == BotStatus.ACTIVE:
                try:
                    # Execute one trading cycle
                    await self._execute_trading_cycle(bot, adapter)

                    # If not infinite loop, stop after one cycle
                    if not bot.infinite_loop:
                        await self._log_activity(
                            bot_id=str(bot.id),
                            level="SUCCESS",
                            message="Trading cycle completed (infinite_loop disabled)"
                        )
                        break

                    # Small delay between cycles
                    await asyncio.sleep(1)

                except Exception as e:
                    await self._handle_bot_error(bot, f"Trading cycle error: {str(e)}")
                    if not bot.infinite_loop:
                        break
                    await asyncio.sleep(5)  # Wait before retry

            # Cleanup
            await adapter.close()

        except asyncio.CancelledError:
            await self._log_activity(
                bot_id=str(bot.id),
                level="INFO",
                message="Bot execution cancelled"
            )
            raise
        except Exception as e:
            await self._handle_bot_error(bot, f"Fatal error: {str(e)}")

    async def _execute_trading_cycle(self, bot: Bot, adapter):
        """
        Execute one complete trading cycle.

        For scalper bot:
        1. Place first order (buy or sell)
        2. Wait for fill
        3. Calculate PnL if selling
        4. Place opposite order
        5. Update bot metrics
        """
        # Determine first order side
        first_side = OrderSide.BUY if bot.first_order == BotOrderSide.BUY else OrderSide.SELL

        # Place first order
        first_order = await self._place_order(
            bot=bot,
            adapter=adapter,
            side=first_side,
            price=Decimal(str(bot.buy_price if first_side == OrderSide.BUY else bot.sell_price))
        )

        if not first_order:
            raise Exception("Failed to place first order")

        # Wait for first order to fill
        await self._wait_for_fill(bot, first_order, adapter)

        # Place second order (opposite side)
        second_side = OrderSide.SELL if first_side == OrderSide.BUY else OrderSide.BUY
        second_order = await self._place_order(
            bot=bot,
            adapter=adapter,
            side=second_side,
            price=Decimal(str(bot.sell_price if second_side == OrderSide.SELL else bot.buy_price))
        )

        if not second_order:
            raise Exception("Failed to place second order")

        # Wait for second order to fill
        await self._wait_for_fill(bot, second_order, adapter)

        # Calculate PnL for the complete cycle
        await self._update_bot_pnl(bot, first_order, second_order)

        # Increment total trades
        bot.total_trades += 2
        bot.last_fill_time = datetime.now()
        await self.db.commit()

    async def _place_order(
        self,
        bot: Bot,
        adapter,
        side: OrderSide,
        price: Decimal
    ) -> Optional[Order]:
        """
        Place an order on the exchange.

        Args:
            bot: Bot instance
            adapter: Exchange adapter
            side: Order side (BUY/SELL)
            price: Order price

        Returns:
            Order instance or None if failed
        """
        try:
            quantity = Decimal(str(bot.quantity))

            # Create order in database
            order = await self.order_manager.create_order(
                bot_id=str(bot.id),
                exchange=bot.exchange.value,
                ticker=bot.ticker,
                side=side,
                order_type=OrderType.LIMIT,
                quantity=quantity,
                price=price
            )

            # Place order on exchange
            result = await adapter.place_order(
                ticker=bot.ticker,
                side=side,
                quantity=quantity,
                order_type=OrderType.LIMIT,
                price=price
            )

            # Update order with exchange response
            await self.order_manager.update_order_from_exchange(order.id, result)

            # Log order placement
            await self._log_activity(
                bot_id=str(bot.id),
                level="INFO",
                message=f"Placed {side.value} order: {quantity} {bot.ticker} @ {price}"
            )

            return order

        except Exception as e:
            await self._log_activity(
                bot_id=str(bot.id),
                level="ERROR",
                message=f"Failed to place {side.value} order: {str(e)}"
            )
            return None

    async def _wait_for_fill(self, bot: Bot, order: Order, adapter, timeout: int = 3600):
        """
        Wait for order to be filled.

        Polls order status until filled or timeout.

        Args:
            bot: Bot instance
            order: Order to monitor
            adapter: Exchange adapter
            timeout: Maximum wait time in seconds (default 1 hour)
        """
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < timeout:
            # Check if bot is still active
            await self.db.refresh(bot)
            if bot.status != BotStatus.ACTIVE:
                raise Exception("Bot stopped while waiting for fill")

            # Get order status from exchange
            status = await adapter.get_order_status(
                order_id=order.exchange_order_id,
                ticker=bot.ticker
            )

            # Update order in database
            await self.order_manager.update_order_from_exchange(order.id, status)

            # Check if filled
            await self.db.refresh(order)
            if order.status == OrderStatus.FILLED:
                await self._log_activity(
                    bot_id=str(bot.id),
                    level="SUCCESS",
                    message=f"{order.side.value} order filled: {order.filled_quantity} @ {order.average_fill_price}"
                )
                return

            # Wait before next poll
            await asyncio.sleep(5)

        # Timeout - cancel order
        await self._log_activity(
            bot_id=str(bot.id),
            level="WARNING",
            message=f"Order timeout - cancelling {order.side.value} order"
        )
        await adapter.cancel_order(order.exchange_order_id, bot.ticker)
        order.status = OrderStatus.CANCELLED
        await self.db.commit()
        raise Exception("Order fill timeout")

    async def _update_bot_pnl(self, bot: Bot, buy_order: Order, sell_order: Order):
        """
        Calculate and update bot PnL based on completed cycle.

        Args:
            bot: Bot instance
            buy_order: Buy order
            sell_order: Sell order
        """
        # Determine which is buy and which is sell
        if buy_order.side == OrderSide.SELL:
            buy_order, sell_order = sell_order, buy_order

        # Calculate PnL
        buy_cost = float(buy_order.average_fill_price or buy_order.price) * float(buy_order.filled_quantity)
        sell_revenue = float(sell_order.average_fill_price or sell_order.price) * float(sell_order.filled_quantity)
        commission = float(buy_order.commission) + float(sell_order.commission)

        cycle_pnl = sell_revenue - buy_cost - commission

        # Update bot PnL
        bot.pnl = (bot.pnl or 0) + cycle_pnl

        # Update orders with PnL
        sell_order.pnl = cycle_pnl

        await self.db.commit()

        # Log PnL
        await self._log_activity(
            bot_id=str(bot.id),
            level="SUCCESS" if cycle_pnl > 0 else "WARNING",
            message=f"Cycle PnL: ${cycle_pnl:.2f} | Total PnL: ${bot.pnl:.2f}"
        )

    async def _get_credentials(self, exchange: str) -> Optional[ExchangeCredentials]:
        """
        Get exchange credentials from database.

        Args:
            exchange: Exchange name

        Returns:
            ExchangeCredentials or None
        """
        result = await self.db.execute(
            select(ExchangeCredentials)
            .where(ExchangeCredentials.exchange == exchange.lower())
            .where(ExchangeCredentials.is_active == True)
        )
        return result.scalar_one_or_none()

    async def _create_adapter(self, credentials: ExchangeCredentials):
        """
        Create exchange adapter from credentials.

        Args:
            credentials: Exchange credentials

        Returns:
            Exchange adapter instance
        """
        # Decrypt API keys
        api_key = decrypt_api_key(credentials.api_key_encrypted)
        secret_key = decrypt_api_key(credentials.secret_key_encrypted)

        # Create adapter
        adapter = create_exchange_adapter(
            exchange_name=credentials.exchange,
            api_key=api_key,
            secret_key=secret_key,
            testnet=credentials.is_testnet
        )

        return adapter

    async def _handle_bot_error(self, bot: Bot, error_message: str):
        """
        Handle bot error by updating status and logging.

        Args:
            bot: Bot instance
            error_message: Error message
        """
        bot.status = BotStatus.ERROR
        await self.db.commit()

        await self._log_activity(
            bot_id=str(bot.id),
            level="ERROR",
            message=error_message
        )

    async def _log_activity(self, bot_id: str, level: str, message: str, extra_data: Dict = None):
        """
        Log activity to database.

        Args:
            bot_id: Bot UUID
            level: Log level (INFO, SUCCESS, WARNING, ERROR)
            message: Log message
            extra_data: Additional data to log
        """
        log = ActivityLog(
            bot_id=bot_id,
            level=level,
            message=message,
            extra_data=extra_data
        )
        self.db.add(log)
        await self.db.commit()
