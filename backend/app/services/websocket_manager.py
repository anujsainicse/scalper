"""
WebSocket Connection Manager for broadcasting application events
"""
from typing import Dict, Set, Any
from fastapi import WebSocket
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections and broadcasts events to all connected clients
    """

    def __init__(self):
        # Set of active WebSocket connections
        self.active_connections: Set[WebSocket] = set()
        logger.info("[WS Manager] Initialized")

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"[WS Manager] Client connected. Total connections: {len(self.active_connections)}")

        # Send welcome message
        await self.send_personal_message(websocket, {
            "type": "system",
            "data": {"message": "Connected to Scalper Bot WebSocket"},
            "timestamp": datetime.utcnow().isoformat()
        })

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        logger.info(f"[WS Manager] Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message to a specific client"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"[WS Manager] Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message_type: str, data: Any):
        """
        Broadcast a message to all connected clients

        Args:
            message_type: Type of message (bot_update, order_filled, etc.)
            data: Message payload
        """
        if not self.active_connections:
            logger.debug(f"[WS Manager] No connections to broadcast {message_type}")
            return

        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"[WS Manager] Broadcasting {message_type} to {len(self.active_connections)} clients")

        # Send to all connections, removing dead ones
        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"[WS Manager] Error broadcasting to client: {e}")
                dead_connections.add(connection)

        # Clean up dead connections
        for connection in dead_connections:
            self.disconnect(connection)

    async def broadcast_bot_update(self, bot_id: str, bot_data: Dict[str, Any]):
        """Broadcast bot update event"""
        await self.broadcast("bot_update", {"id": bot_id, **bot_data})

    async def broadcast_bot_created(self, bot_data: Dict[str, Any]):
        """Broadcast bot creation event"""
        await self.broadcast("bot_created", bot_data)

    async def broadcast_bot_deleted(self, bot_id: str):
        """Broadcast bot deletion event"""
        await self.broadcast("bot_deleted", {"id": bot_id})

    async def broadcast_order_update(self, order_data: Dict[str, Any]):
        """Broadcast order update event"""
        await self.broadcast("order_update", order_data)

    async def broadcast_order_filled(self, order_data: Dict[str, Any]):
        """Broadcast order filled event"""
        await self.broadcast("order_filled", order_data)

    async def broadcast_log_created(self, log_data: Dict[str, Any]):
        """Broadcast activity log creation event"""
        await self.broadcast("log_created", log_data)

    async def broadcast_pnl_update(self, bot_id: str, pnl: float):
        """Broadcast PnL update event"""
        await self.broadcast("pnl_update", {"bot_id": bot_id, "pnl": pnl})

    async def broadcast_price_update(self, ticker: str, price: float, exchange: str):
        """Broadcast price update event"""
        await self.broadcast("price_update", {
            "ticker": ticker,
            "price": price,
            "exchange": exchange
        })


# Global instance
ws_manager = WebSocketManager()
