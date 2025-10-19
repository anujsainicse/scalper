"""Redis client configuration and utilities"""
import redis.asyncio as redis
from typing import Optional, Dict, Any
from app.core.config import settings


class RedisClient:
    """Redis client for fetching LTP and price data"""

    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis"""
        if not self.client:
            self.client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()

    async def get_price_data(self, redis_key: str) -> Dict[str, Any]:
        """
        Fetch price data from Redis using HGETALL

        Args:
            redis_key: The Redis key (e.g., 'coindcx_futures:ETH')

        Returns:
            Dictionary with price data fields (ltp, current_funding_rate, timestamp, etc.)
        """
        if not self.client:
            await self.connect()

        data = await self.client.hgetall(redis_key)
        return data if data else {}


# Global Redis client instance
redis_client = RedisClient()


async def get_redis_client() -> RedisClient:
    """Dependency to get Redis client"""
    if not redis_client.client:
        await redis_client.connect()
    return redis_client
