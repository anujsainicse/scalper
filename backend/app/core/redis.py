"""Redis client configuration and utilities"""
import redis
from typing import Dict, Any
from app.core.config import settings


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


# Global Redis client instance
redis_client = RedisClient()


def get_redis_client() -> RedisClient:
    """Dependency to get Redis client"""
    if not redis_client.client:
        redis_client.connect()
    return redis_client
