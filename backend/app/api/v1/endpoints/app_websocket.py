"""
WebSocket endpoint for real-time application updates (bot status, orders, logs, etc.)
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import ws_manager
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/app")
async def websocket_app_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time application updates

    Broadcasts:
    - bot_update: When bot status/config changes
    - bot_created: When new bot is created
    - bot_deleted: When bot is deleted
    - order_update: When order status changes
    - order_filled: When order is filled
    - log_created: When activity log is created
    - pnl_update: When bot PnL changes
    - price_update: When ticker price updates
    """
    await ws_manager.connect(websocket)

    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()

            # Handle ping/pong
            if data == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": ""
                }))
                continue

            # Parse other messages
            try:
                message = json.loads(data)
                message_type = message.get("type")

                if message_type == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": ""
                    }))
                else:
                    logger.info(f"[App WS] Received message: {message_type}")

            except json.JSONDecodeError:
                logger.warning(f"[App WS] Invalid JSON received: {data}")

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info("[App WS] Client disconnected normally")
    except Exception as e:
        logger.error(f"[App WS] Error: {e}")
        ws_manager.disconnect(websocket)
