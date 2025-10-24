"""Redis client configuration and utilities"""
import redis
import redis.asyncio as aioredis
from typing import Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for fetching LTP and price data (synchronous for reliability)"""

    def __init__(self):
        self.client = None

    def connect(self):
        """Connect to Redis"""
        if not self.client:
            try:
                self.client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2,  # 2 second connection timeout
                    socket_timeout=2,           # 2 second operation timeout
                )
                # Test connection
                self.client.ping()
            except Exception as e:
                raise Exception(f"Failed to connect to Redis: {str(e)}")

    def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            self.client.close()

    def get_price_data(self, redis_key: str) -> Dict[str, Any]:
        """
        Fetch price data from Redis using HGETALL

        Args:
            redis_key: The Redis key (e.g., 'coindcx_futures:ETH')

        Returns:
            Dictionary with price data fields (ltp, current_funding_rate, timestamp, etc.)
        """
        if not self.client:
            self.connect()

        try:
            data = self.client.hgetall(redis_key)
            return data if data else {}
        except Exception as e:
            raise Exception(f"Redis error: {str(e)}")


class AsyncRedisClient:
    """Async Redis client for non-blocking operations"""

    def __init__(self):
        self.client: Optional[aioredis.Redis] = None
        self._pool: Optional[aioredis.ConnectionPool] = None

    async def connect(self):
        """Connect to Redis with connection pooling"""
        if not self.client:
            try:
                # Create connection pool for better performance
                self._pool = aioredis.ConnectionPool.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=20,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )

                self.client = aioredis.Redis(connection_pool=self._pool)

                # Test connection
                await self.client.ping()
                logger.info("[Async Redis] Connected successfully")
            except Exception as e:
                logger.error(f"[Async Redis] Connection failed: {e}")
                raise Exception(f"Failed to connect to Redis: {str(e)}")

    async def disconnect(self):
        """Disconnect from Redis and close pool"""
        if self.client:
            await self.client.close()
        if self._pool:
            await self._pool.disconnect()
        logger.info("[Async Redis] Disconnected")

    async def get_price_data(self, redis_key: str) -> Dict[str, Any]:
        """
        Fetch price data from Redis using HGETALL (async)

        Args:
            redis_key: The Redis key (e.g., 'coindcx_futures:ETH')

        Returns:
            Dictionary with price data fields (ltp, current_funding_rate, timestamp, etc.)
        """
        if not self.client:
            await self.connect()

        try:
            data = await self.client.hgetall(redis_key)
            return data if data else {}
        except Exception as e:
            logger.error(f"[Async Redis] Error fetching {redis_key}: {e}")
            raise Exception(f"Redis error: {str(e)}")

    async def get(self, key: str) -> Optional[str]:
        """Get a simple string value from Redis"""
        if not self.client:
            await self.connect()

        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"[Async Redis] Error getting {key}: {e}")
            return None

    async def set(self, key: str, value: str, ex: int = None):
        """Set a simple string value in Redis with optional expiry"""
        if not self.client:
            await self.connect()

        try:
            await self.client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"[Async Redis] Error setting {key}: {e}")


# Global Redis client instances
redis_client = RedisClient()
async_redis_client = AsyncRedisClient()


def get_redis_client() -> RedisClient:
    """Dependency to get sync Redis client"""
    if not redis_client.client:
        redis_client.connect()
    return redis_client


async def get_async_redis_client() -> AsyncRedisClient:
    """Dependency to get async Redis client"""
    if not async_redis_client.client:
        await async_redis_client.connect()
    return async_redis_client
