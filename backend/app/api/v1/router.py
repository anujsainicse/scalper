from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    api_keys,
    bots,
    logs,
    telegram,
    price,
    orders,
    websocket,
    app_websocket,
    analytics
)

api_router = APIRouter()

# Authentication & User Management (NEW - Multi-user support)
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])

# Existing endpoints (now with authentication)
api_router.include_router(bots.router, prefix="/bots", tags=["bots"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(logs.router, prefix="/logs", tags=["activity-logs"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
api_router.include_router(price.router, prefix="/price", tags=["price"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(app_websocket.router, tags=["app-websocket"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
