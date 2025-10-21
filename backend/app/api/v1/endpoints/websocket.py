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
        """Connect to CoinDCX WebSocket"""
        try:
            logger.info("Connecting to CoinDCX WebSocket...")
            self.coindcx_client = CoinDCXFutures()

            # Connect to WebSocket FIRST (this creates self.sio)
            await self.coindcx_client.connect_websocket()

            # Register event handlers AFTER connection (requires self.sio to exist)
            self.coindcx_client.on_order_update(self.handle_order_update)
            self.coindcx_client.on_position_update(self.handle_position_update)
            self.coindcx_client.on_balance_update(self.handle_balance_update)

            self.coindcx_connected = True

            logger.info("✅ Connected to CoinDCX WebSocket and registered handlers")

        except Exception as e:
            logger.error(f"❌ Failed to connect to CoinDCX: {e}")
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
        try:
            # Parse the data - CoinDCX sends it as a JSON string
            if isinstance(data, dict) and 'data' in data:
                order_list = json.loads(data['data'])
                order_data = order_list[0] if order_list else {}
            else:
                order_data = data

            # Create event message
            event = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "type": "order",
                "data": {
                    "id": order_data.get("id"),
                    "pair": order_data.get("pair"),
                    "side": order_data.get("side"),
                    "status": order_data.get("status"),
                    "order_type": order_data.get("order_type"),
                    "price": float(order_data.get("price", 0)),
                    "total_quantity": float(order_data.get("total_quantity", 0)),
                    "filled_quantity": float(order_data.get("filled_quantity", 0)),
                    "remaining_quantity": float(order_data.get("remaining_quantity", 0)),
                    "leverage": order_data.get("leverage"),
                    "display_message": order_data.get("display_message"),
                    "created_at": order_data.get("created_at"),
                }
            }

            logger.info(f"📦 Order Update: {order_data.get('id')} - {order_data.get('status')}")
            await self.broadcast(event)

            # Check if order is filled - trigger opposite order placement
            order_status = order_data.get("status", "").lower()
            if order_status == "filled":
                filled_qty = float(order_data.get("filled_quantity", 0))
                total_qty = float(order_data.get("total_quantity", 0))

                # Only process if completely filled
                if filled_qty >= total_qty and total_qty > 0:
                    logger.info(
                        f"🎯 Order {order_data.get('id')} is FILLED. "
                        f"Processing opposite order placement..."
                    )

                    # Process the fill in a background task to avoid blocking WebSocket
                    asyncio.create_task(self._process_filled_order(
                        exchange_order_id=order_data.get("id"),
                        filled_quantity=filled_qty,
                        total_quantity=total_qty,
                        filled_price=float(order_data.get("avg_price", order_data.get("price", 0)))
                    ))

        except Exception as e:
            logger.error(f"Error handling order update: {e}")

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
        try:
            # Create a new database session for this task
            async with AsyncSessionLocal() as db:
                success = await process_order_fill(
                    exchange_order_id=exchange_order_id,
                    filled_quantity=filled_quantity,
                    total_quantity=total_quantity,
                    filled_price=filled_price,
                    db=db
                )

                if success:
                    logger.info(f"✅ Successfully processed filled order {exchange_order_id}")
                else:
                    logger.warning(f"⚠️ Failed to process filled order {exchange_order_id}")

        except Exception as e:
            logger.error(f"❌ Error in background task for order {exchange_order_id}: {e}")

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
