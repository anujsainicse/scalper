"""
WebSocket endpoints for real-time data streaming
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json
import uuid
from datetime import datetime
import logging

from app.exchanges.coindcx.client import CoinDCXFutures
from app.db.session import AsyncSessionLocal
from app.services.order_monitor import process_order_fill

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Track active WebSocket connections
active_connections: Set[WebSocket] = set()


class ConnectionManager:
    """Manages WebSocket connections and broadcasting"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.coindcx_client: CoinDCXFutures | None = None
        self.coindcx_connected: bool = False

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

        # Start CoinDCX connection if not already connected
        if not self.coindcx_connected:
            await self.connect_coindcx()

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

        # Disconnect from CoinDCX if no more connections
        if len(self.active_connections) == 0 and self.coindcx_client:
            asyncio.create_task(self.disconnect_coindcx())

    async def connect_coindcx(self):
        """
        Connect to CoinDCX WebSocket with proper handler registration order

        CRITICAL: Socket.IO requires handlers to be registered BEFORE connecting.
        Correct order:
        1. Create CoinDCXFutures client
        2. Initialize Socket.IO client (creates self.sio object)
        3. Register event handlers using @self.sio.on() decorators
        4. Connect to WebSocket
        """
        try:
            logger.info("🔌 [STEP 1] Creating CoinDCXFutures client...")
            self.coindcx_client = CoinDCXFutures()
            logger.info(f"✅ [STEP 1] CoinDCXFutures client created: {self.coindcx_client is not None}")

            # STEP 2: Initialize Socket.IO client (creates self.sio) WITHOUT connecting
            logger.info("🔌 [STEP 2] Initializing Socket.IO client...")
            sio = self.coindcx_client.init_websocket_client()
            logger.info(f"✅ [STEP 2] Socket.IO client initialized. sio exists: {sio is not None}")

            # STEP 3: Register event handlers BEFORE connecting (Socket.IO requirement!)
            logger.info("📋 [STEP 3] Registering event handlers BEFORE connection...")
            logger.info(f"   Handler function exists: {self.handle_order_update is not None}")
            logger.info(f"   sio object exists: {self.coindcx_client.sio is not None}")

            self.coindcx_client.on_order_update(self.handle_order_update)
            logger.info("✅ [STEP 3a] Order update handler registered")

            self.coindcx_client.on_position_update(self.handle_position_update)
            logger.info("✅ [STEP 3b] Position update handler registered")

            self.coindcx_client.on_balance_update(self.handle_balance_update)
            logger.info("✅ [STEP 3c] Balance update handler registered")

            # STEP 4: NOW connect to WebSocket (handlers are already registered)
            logger.info("🔌 [STEP 4] Connecting to CoinDCX WebSocket with handlers registered...")
            await self.coindcx_client.connect_websocket()
            logger.info(f"✅ [STEP 4] WebSocket connected successfully")

            self.coindcx_connected = True

            logger.info("✅ [COMPLETE] CoinDCX WebSocket fully connected with event handlers")
            logger.info(f"   Connection status: {self.coindcx_connected}")
            logger.info(f"   Waiting for order events on channel: df-order-update")
            logger.info(f"   NOTE: Handlers were registered BEFORE connecting (correct order)")

        except Exception as e:
            logger.error(f"❌ Failed to connect to CoinDCX: {e}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback:\n{traceback.format_exc()}")
            self.coindcx_connected = False

    async def disconnect_coindcx(self):
        """Disconnect from CoinDCX WebSocket"""
        if self.coindcx_client:
            try:
                await self.coindcx_client.disconnect_websocket()
                logger.info("Disconnected from CoinDCX WebSocket")
            except Exception as e:
                logger.error(f"Error disconnecting from CoinDCX: {e}")
            finally:
                self.coindcx_client = None
                self.coindcx_connected = False

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def handle_order_update(self, data: dict):
        """Handle order update from CoinDCX"""
        logger.info("🔔 ========== ORDER UPDATE EVENT RECEIVED ==========")
        logger.info(f"🔔 [EVENT] Raw data type: {type(data)}")
        logger.info(f"🔔 [EVENT] Handler called successfully!")

        try:
            # Parse the data - CoinDCX sends it as a JSON string
            if isinstance(data, dict) and 'data' in data:
                logger.info(f"🔍 [PARSE] Data has 'data' key, parsing JSON...")
                order_list = json.loads(data['data'])
                order_data = order_list[0] if order_list else {}
                logger.info(f"✅ [PARSE] Extracted order data from list")
            else:
                logger.info(f"🔍 [PARSE] Using data directly (no 'data' key)")
                order_data = data

            order_id = order_data.get("id")
            order_status = order_data.get("status", "").lower()
            filled_qty = float(order_data.get("filled_quantity", 0))
            total_qty = float(order_data.get("total_quantity", 0))

            logger.info(f"📋 [ORDER INFO]:")
            logger.info(f"   Order ID: {order_id}")
            logger.info(f"   Status: {order_status}")
            logger.info(f"   Filled: {filled_qty}/{total_qty}")
            logger.info(f"   Pair: {order_data.get('pair')}")
            logger.info(f"   Side: {order_data.get('side')}")

            # Query database to get bot_id for this order
            bot_id = None
            try:
                from app.models.order import Order as OrderModel
                from sqlalchemy import select

                async with AsyncSessionLocal() as db:
                    result = await db.execute(
                        select(OrderModel).where(OrderModel.exchange_order_id == order_id)
                    )
                    order = result.scalar_one_or_none()
                    if order:
                        bot_id = str(order.bot_id)
                        logger.info(f"📋 [ORDER INFO] Bot ID: {bot_id}")
                    else:
                        logger.warning(f"⚠️ [ORDER INFO] Order {order_id} not found in database")
            except Exception as e:
                logger.error(f"❌ [ERROR] Failed to query bot_id: {e}")

            # Create event message
            event = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "type": "order",
                "data": {
                    "id": order_id,
                    "bot_id": bot_id,
                    "pair": order_data.get("pair"),
                    "side": order_data.get("side"),
                    "status": order_data.get("status"),
                    "order_type": order_data.get("order_type"),
                    "price": float(order_data.get("price", 0)),
                    "total_quantity": total_qty,
                    "filled_quantity": filled_qty,
                    "remaining_quantity": float(order_data.get("remaining_quantity", 0)),
                    "leverage": order_data.get("leverage"),
                    "display_message": order_data.get("display_message"),
                    "created_at": order_data.get("created_at"),
                }
            }

            logger.info(f"📤 [BROADCAST] Broadcasting to {len(self.active_connections)} WebSocket clients")
            await self.broadcast(event)

            # Check if order is filled - trigger opposite order placement
            logger.info(f"🔍 [FILL CHECK] Checking if order should trigger opposite placement...")
            logger.info(f"   Status == 'filled'? {order_status == 'filled'}")
            logger.info(f"   Filled >= Total? {filled_qty >= total_qty}")
            logger.info(f"   Total > 0? {total_qty > 0}")

            if order_status == "filled":
                logger.info(f"✅ [FILL CHECK] Status is 'filled', checking quantity...")

                # CoinDCX WebSocket sometimes sends filled_quantity as 0 even when status is "filled"
                # In this case, trust the status and use total_quantity
                if filled_qty == 0 and total_qty > 0:
                    logger.warning(f"⚠️ [QUIRK] filled_quantity is 0 but status is 'filled' - using total_quantity")
                    filled_qty = total_qty

                # Only process if completely filled
                if filled_qty >= total_qty and total_qty > 0:
                    logger.info(f"🎯 ========== FILL DETECTED ==========")
                    logger.info(f"🎯 [TRIGGER] Order {order_id} is COMPLETELY FILLED!")
                    logger.info(f"🎯 [TRIGGER] Filled: {filled_qty}, Total: {total_qty}")
                    logger.info(f"🎯 [TRIGGER] Starting opposite order placement process...")

                    avg_price = float(order_data.get("avg_price", order_data.get("price", 0)))
                    logger.info(f"🎯 [TRIGGER] Fill price: ${avg_price}")

                    # Process the fill in a background task to avoid blocking WebSocket
                    logger.info(f"🚀 [ASYNC] Creating background task for opposite order placement...")
                    asyncio.create_task(self._process_filled_order(
                        exchange_order_id=order_id,
                        filled_quantity=filled_qty,
                        total_quantity=total_qty,
                        filled_price=avg_price
                    ))
                    logger.info(f"✅ [ASYNC] Background task created successfully")
                else:
                    logger.warning(f"⚠️ [SKIP] Order {order_id} status is 'filled' but quantity check failed:")
                    logger.warning(f"   Filled: {filled_qty}, Total: {total_qty}")
                    logger.warning(f"   filled_qty >= total_qty: {filled_qty >= total_qty}")
                    logger.warning(f"   total_qty > 0: {total_qty > 0}")
            elif order_status == "cancelled":
                logger.warning(f"⚠️ ========== CANCELLATION DETECTED ==========")
                logger.warning(f"⚠️ [CANCELLED] Order {order_id} was cancelled on exchange")
                logger.warning(f"⚠️ [CANCELLED] Bot will be stopped automatically")

                # Process cancellation in background task
                logger.info(f"🚀 [ASYNC] Creating background task for cancellation handling...")
                asyncio.create_task(self._process_cancelled_order(
                    exchange_order_id=order_id
                ))
                logger.info(f"✅ [ASYNC] Cancellation handler task created successfully")
            else:
                logger.info(f"ℹ️ [SKIP] Order status is '{order_status}', not 'filled' or 'cancelled'. No action needed.")

            logger.info(f"📦 ========== ORDER UPDATE PROCESSING COMPLETE ==========\n")

        except Exception as e:
            logger.error(f"❌ ========== ERROR IN ORDER UPDATE HANDLER ==========")
            logger.error(f"❌ [ERROR] Exception: {e}")
            logger.error(f"❌ [ERROR] Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ [ERROR] Traceback:\n{traceback.format_exc()}")
            logger.error(f"❌ ==========================================================\n")

    async def _process_filled_order(
        self,
        exchange_order_id: str,
        filled_quantity: float,
        total_quantity: float,
        filled_price: float
    ):
        """
        Process a filled order in a background task

        This runs asynchronously to avoid blocking the WebSocket connection
        """
        logger.info(f"🚀 ========== BACKGROUND TASK STARTED ==========")
        logger.info(f"🚀 [TASK] Processing filled order: {exchange_order_id}")
        logger.info(f"🚀 [TASK] Parameters:")
        logger.info(f"   - Order ID: {exchange_order_id}")
        logger.info(f"   - Filled Qty: {filled_quantity}")
        logger.info(f"   - Total Qty: {total_quantity}")
        logger.info(f"   - Fill Price: ${filled_price}")

        try:
            # Create a new database session for this task
            logger.info(f"💾 [DB] Creating new database session...")
            async with AsyncSessionLocal() as db:
                logger.info(f"✅ [DB] Database session created successfully")
                logger.info(f"📞 [CALL] Calling process_order_fill() from order_monitor.py...")

                success = await process_order_fill(
                    exchange_order_id=exchange_order_id,
                    filled_quantity=filled_quantity,
                    total_quantity=total_quantity,
                    filled_price=filled_price,
                    db=db
                )

                logger.info(f"📞 [CALL] process_order_fill() returned: {success}")

                if success:
                    logger.info(f"✅ ========== OPPOSITE ORDER PLACED SUCCESSFULLY ==========")
                    logger.info(f"✅ [SUCCESS] Order {exchange_order_id} processed")
                    logger.info(f"✅ [SUCCESS] Opposite order should now be on exchange")
                    logger.info(f"✅ ==========================================================\n")
                else:
                    logger.warning(f"⚠️ ========== OPPOSITE ORDER PLACEMENT FAILED ==========")
                    logger.warning(f"⚠️ [FAILURE] Order {exchange_order_id} processing failed")
                    logger.warning(f"⚠️ [FAILURE] Check order_monitor.py logs for details")
                    logger.warning(f"⚠️ ==========================================================\n")

        except Exception as e:
            logger.error(f"❌ ========== BACKGROUND TASK EXCEPTION ==========")
            logger.error(f"❌ [EXCEPTION] Order: {exchange_order_id}")
            logger.error(f"❌ [EXCEPTION] Error: {e}")
            logger.error(f"❌ [EXCEPTION] Type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ [EXCEPTION] Traceback:\n{traceback.format_exc()}")
            logger.error(f"❌ ==========================================================\n")

    async def _process_cancelled_order(
        self,
        exchange_order_id: str
    ):
        """
        Process a cancelled order by stopping the bot
        (ONLY if it's a manual cancellation, not system-initiated)

        When an order is cancelled on the exchange, we need to:
        1. Check if cancellation was system-initiated (UPDATE/STOP/DELETE)
        2. If manual cancellation:
           - Update the order status to CANCELLED
           - Stop the bot (set status to STOPPED)
           - Log the activity
           - Send notification
        3. If system-initiated: Just update order status, don't stop bot

        Args:
            exchange_order_id: The exchange order ID that was cancelled
        """
        logger.info(f"🛑 ========== PROCESSING CANCELLED ORDER ==========")
        logger.info(f"🛑 [CANCELLED] Order ID: {exchange_order_id}")

        try:
            # Create a new database session for this task
            logger.info(f"💾 [DB] Creating new database session...")
            async with AsyncSessionLocal() as db:
                logger.info(f"✅ [DB] Database session created successfully")

                # Import models
                from app.models.order import Order as OrderModel, OrderStatus
                from app.models.bot import Bot, BotStatus, ActivityLog
                from sqlalchemy import select

                # Find the order
                logger.info(f"🔍 [DB] Searching for order {exchange_order_id}...")
                result = await db.execute(
                    select(OrderModel).where(OrderModel.exchange_order_id == exchange_order_id)
                )
                order = result.scalar_one_or_none()

                if not order:
                    logger.warning(f"⚠️ [CANCELLED] Order {exchange_order_id} not found in database")
                    return

                logger.info(f"✅ [DB] Order found: {order.id}")
                logger.info(f"🔍 [DB] Cancellation reason: {order.cancellation_reason}")

                # Update order status to CANCELLED
                order.status = OrderStatus.CANCELLED
                logger.info(f"✅ [CANCELLED] Order status updated to CANCELLED")

                # CHECK CANCELLATION REASON - Don't auto-stop for system cancellations
                if order.cancellation_reason in ["UPDATE", "STOP", "DELETE"]:
                    logger.info(f"ℹ️ ========== SYSTEM-INITIATED CANCELLATION ==========")
                    logger.info(f"ℹ️ [CANCELLED] Reason: {order.cancellation_reason}")
                    logger.info(f"ℹ️ [CANCELLED] This is expected - bot operation in progress")
                    logger.info(f"ℹ️ [CANCELLED] Order marked as CANCELLED, bot will remain in current state")

                    # Just commit the order status change
                    await db.commit()

                    # Log the system cancellation for audit trail
                    log = ActivityLog(
                        bot_id=order.bot_id,
                        level="INFO",
                        message=f"Order cancelled for {order.cancellation_reason.lower()} operation"
                    )
                    db.add(log)
                    await db.commit()

                    logger.info(f"✅ [CANCELLED] System cancellation processed, bot not affected")
                    logger.info(f"✅ ==========================================================\n")
                    return

                # If no reason or other reason, this is a manual cancellation - proceed with auto-stop
                logger.warning(f"⚠️ ========== MANUAL CANCELLATION DETECTED ==========")
                logger.warning(f"⚠️ [CANCELLED] Reason: {order.cancellation_reason or 'None (manual)'}")
                logger.warning(f"⚠️ [CANCELLED] Bot will be stopped automatically")

                # Get the bot
                logger.info(f"🔍 [DB] Fetching bot {order.bot_id}...")
                bot_result = await db.execute(select(Bot).where(Bot.id == order.bot_id))
                bot = bot_result.scalar_one_or_none()

                if not bot:
                    logger.error(f"❌ [CANCELLED] Bot {order.bot_id} not found")
                    await db.commit()
                    return

                logger.info(f"✅ [DB] Bot found: {bot.ticker} (current status: {bot.status.value})")

                # Stop the bot
                bot.status = BotStatus.STOPPED
                logger.info(f"✅ [CANCELLED] Bot {bot.id} status set to STOPPED")

                # Create activity log
                log = ActivityLog(
                    bot_id=bot.id,
                    level="WARNING",
                    message=f"Bot stopped automatically - {order.side.value} order cancelled on exchange"
                )
                db.add(log)
                logger.info(f"✅ [LOG] Activity log created")

                # Commit changes
                await db.commit()
                logger.info(f"✅ [DB] Database changes committed")

                # Send Telegram notification
                logger.info(f"📤 [TELEGRAM] Sending notification...")
                from app.services.telegram import telegram_service
                await telegram_service.send_notification(
                    db=db,
                    message=f"*⚠️ Bot Auto-Stopped*\n\n"
                            f"Bot: {bot.ticker}\n"
                            f"Reason: Order cancelled on exchange\n"
                            f"Order ID: {exchange_order_id}\n"
                            f"Status: STOPPED",
                    level="WARNING"
                )
                logger.info(f"✅ [TELEGRAM] Notification sent")

                logger.info(f"✅ ========== BOT STOPPED DUE TO CANCELLATION ==========")
                logger.info(f"✅ [SUCCESS] Bot {bot.ticker} successfully stopped")
                logger.info(f"✅ ==========================================================\n")

        except Exception as e:
            logger.error(f"❌ ========== CANCELLATION PROCESSING EXCEPTION ==========")
            logger.error(f"❌ [EXCEPTION] Order: {exchange_order_id}")
            logger.error(f"❌ [EXCEPTION] Error: {e}")
            logger.error(f"❌ [EXCEPTION] Type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ [EXCEPTION] Traceback:\n{traceback.format_exc()}")
            logger.error(f"❌ ==========================================================\n")

    async def handle_position_update(self, data: dict):
        """Handle position update from CoinDCX"""
        try:
            # Parse the data
            if isinstance(data, dict) and 'data' in data:
                position_list = json.loads(data['data'])
                position_data = position_list[0] if position_list else {}
            else:
                position_data = data

            # Create event message
            event = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "type": "position",
                "data": {
                    "id": position_data.get("id"),
                    "pair": position_data.get("pair"),
                    "active_pos": float(position_data.get("active_pos", 0)),
                    "avg_price": float(position_data.get("avg_price", 0)),
                    "liquidation_price": float(position_data.get("liquidation_price", 0)),
                    "locked_margin": float(position_data.get("locked_margin", 0)),
                    "unrealized_pnl": float(position_data.get("unrealized_pnl", 0)) if position_data.get("unrealized_pnl") else None,
                }
            }

            logger.info(f"📊 Position Update: {position_data.get('pair')}")
            await self.broadcast(event)

        except Exception as e:
            logger.error(f"Error handling position update: {e}")

    async def handle_balance_update(self, data: dict):
        """Handle balance update from CoinDCX"""
        try:
            # Parse the data
            if isinstance(data, dict) and 'data' in data:
                balance_list = json.loads(data['data'])
                balance_data = balance_list[0] if balance_list else {}
            else:
                balance_data = data

            # Create event message
            event = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "type": "balance",
                "data": {
                    "currency_short_name": balance_data.get("currency_short_name"),
                    "balance": balance_data.get("balance"),
                    "locked_balance": balance_data.get("locked_balance"),
                }
            }

            logger.info(f"💰 Balance Update: {balance_data.get('currency_short_name')}")
            await self.broadcast(event)

        except Exception as e:
            logger.error(f"Error handling balance update: {e}")


# Create a global connection manager
manager = ConnectionManager()


@router.websocket("/coindcx")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time CoinDCX data

    Connects to CoinDCX Futures WebSocket and forwards events to frontend clients.

    Events sent to clients:
    - order: Order updates (placed, filled, cancelled)
    - position: Position updates (opens, closes, PnL changes)
    - balance: Balance updates (available, locked)
    """
    await manager.connect(websocket)

    try:
        # Send connection success message
        await websocket.send_json({
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "type": "system",
            "data": {
                "message": "Connected to CoinDCX WebSocket bridge",
                "coindcx_connected": manager.coindcx_connected
            }
        })

        # Keep connection alive
        while True:
            # Wait for messages from client (ping/pong)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)

                # Handle client messages if needed
                if data == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })

            except asyncio.TimeoutError:
                # Send ping to check if connection is alive
                await websocket.send_json({
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        logger.info("Client disconnected normally")
        manager.disconnect(websocket)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.get("/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "active_connections": len(manager.active_connections),
        "coindcx_connected": manager.coindcx_connected,
    }
