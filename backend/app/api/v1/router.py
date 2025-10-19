from fastapi import APIRouter
from app.api.v1.endpoints import bots, logs, telegram, price

api_router = APIRouter()

api_router.include_router(bots.router, prefix="/bots", tags=["bots"])
api_router.include_router(logs.router, prefix="/logs", tags=["activity-logs"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
api_router.include_router(price.router, prefix="/price", tags=["price"])
