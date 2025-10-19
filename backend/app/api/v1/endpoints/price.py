from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any
from app.core.redis import get_redis_client, RedisClient

router = APIRouter()


@router.get("/ltp")
def get_ltp_data(
    exchange: str = Query(..., description="Exchange name (e.g., 'CoinDCX F')"),
    ticker: str = Query(..., description="Trading ticker symbol (e.g., 'ETH/USDT')"),
    redis_client: RedisClient = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Get Last Traded Price (LTP) and related data from Redis

    The exchange parameter is mapped to Redis prefix using the frontend config.
    For example: 'CoinDCX F' -> 'coindcx_futures'

    The ticker is extracted to get the base symbol (e.g., 'ETH/USDT' -> 'ETH')

    Final Redis key format: {redis_prefix}:{base_symbol}
    Example: 'coindcx_futures:ETH'
    """
    try:
        # Map exchange to Redis prefix
        exchange_mapping = {
            'CoinDCX F': 'coindcx_futures',
            'Binance': 'binance_spot',
            'Delta': 'delta_futures',
            'Bybit': 'bybit_spot'
        }

        redis_prefix = exchange_mapping.get(exchange)
        if not redis_prefix:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown exchange: {exchange}"
            )

        # Extract base symbol from ticker (e.g., 'ETH/USDT' -> 'ETH')
        base_symbol = ticker.split('/')[0] if '/' in ticker else ticker

        # Build Redis key
        redis_key = f"{redis_prefix}:{base_symbol}"

        # Fetch data from Redis
        data = redis_client.get_price_data(redis_key)

        if not data:
            return {
                "success": False,
                "message": f"No data found for {ticker} on {exchange}",
                "redis_key": redis_key,
                "data": {}
            }

        return {
            "success": True,
            "redis_key": redis_key,
            "exchange": exchange,
            "ticker": ticker,
            "base_symbol": base_symbol,
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
