"""
CoinDCX Futures Exchange Adapter

Implements the BaseExchangeAdapter for CoinDCX Futures exchange.
Integrates with coindcx-futures repository for actual API calls.
"""

from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
import httpx
import hmac
import hashlib
import json
import time

from app.exchanges.base import BaseExchangeAdapter, OrderType, OrderStatus, OrderSide


class CoinDCXAdapter(BaseExchangeAdapter):
    """
    CoinDCX Futures exchange adapter.

    TODO: Integrate with coindcx-futures repository client.
    For now, this is a working skeleton showing the adapter pattern.
    """

    def __init__(self, api_key: str, secret_key: str, testnet: bool = True, **kwargs):
        super().__init__(api_key, secret_key, testnet, **kwargs)

        # Set base URL based on testnet flag
        if testnet:
            self.base_url = "https://public-api.coindcx.com"  # CoinDCX doesn't have separate testnet
        else:
            self.base_url = "https://api.coindcx.com"

        self.client = httpx.AsyncClient(timeout=30.0)

    @property
    def exchange_name(self) -> str:
        return "coindcx"

    def _generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for authenticated requests"""
        return hmac.new(
            self.secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        authenticated: bool = False
    ) -> Dict[str, Any]:
        """Make HTTP request to CoinDCX API"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        if authenticated:
            timestamp = str(int(time.time() * 1000))
            payload = json.dumps(data or {})

            headers.update({
                "X-AUTH-APIKEY": self.api_key,
                "X-AUTH-SIGNATURE": self._generate_signature(payload),
                "X-AUTH-TIMESTAMP": timestamp
            })

        try:
            if method == "GET":
                response = await self.client.get(url, params=params, headers=headers)
            elif method == "POST":
                response = await self.client.post(url, json=data, headers=headers)
            elif method == "DELETE":
                response = await self.client.delete(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"CoinDCX API error: {str(e)}")

    async def validate_credentials(self) -> bool:
        """Validate API credentials by fetching account balance"""
        try:
            # Try to fetch account info
            response = await self._make_request(
                "POST",
                "/exchange/v1/users/balances",
                authenticated=True
            )
            return isinstance(response, list)
        except Exception:
            return False

    async def place_order(
        self,
        ticker: str,
        side: OrderSide,
        quantity: Decimal,
        order_type: OrderType = OrderType.LIMIT,
        price: Optional[Decimal] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Place an order on CoinDCX Futures.

        TODO: Implement using coindcx-futures client.
        """
        # Format ticker (ETH/USDT -> ETHUSDT)
        market = self.format_ticker(ticker)

        # Prepare order payload
        order_data = {
            "market": market,
            "side": side.value.lower(),  # buy or sell
            "order_type": "limit_order" if order_type == OrderType.LIMIT else "market_order",
            "quantity": float(quantity),
            "timestamp": int(time.time() * 1000)
        }

        if order_type == OrderType.LIMIT and price:
            order_data["price_per_unit"] = float(price)

        try:
            response = await self._make_request(
                "POST",
                "/exchange/v1/orders/create",
                data=order_data,
                authenticated=True
            )

            return {
                "order_id": response.get("id"),
                "status": OrderStatus.OPEN,
                "filled_quantity": Decimal("0"),
                "average_price": price or Decimal("0"),
                "created_at": datetime.now(),
                "raw_response": response
            }
        except Exception as e:
            return {
                "order_id": None,
                "status": OrderStatus.FAILED,
                "error": str(e),
                "raw_response": {}
            }

    async def cancel_order(self, order_id: str, ticker: str) -> Dict[str, Any]:
        """Cancel an existing order"""
        try:
            response = await self._make_request(
                "POST",
                "/exchange/v1/orders/cancel",
                data={"id": order_id},
                authenticated=True
            )
            return response
        except Exception as e:
            raise Exception(f"Failed to cancel order: {str(e)}")

    async def get_order_status(self, order_id: str, ticker: str) -> Dict[str, Any]:
        """Get status of an order"""
        try:
            response = await self._make_request(
                "POST",
                "/exchange/v1/orders/status",
                data={"id": order_id},
                authenticated=True
            )

            # Map CoinDCX status to our OrderStatus
            status_map = {
                "open": OrderStatus.OPEN,
                "partially_filled": OrderStatus.PARTIALLY_FILLED,
                "filled": OrderStatus.FILLED,
                "cancelled": OrderStatus.CANCELLED,
                "rejected": OrderStatus.REJECTED
            }

            return {
                "order_id": order_id,
                "status": status_map.get(response.get("status", "open"), OrderStatus.OPEN),
                "filled_quantity": Decimal(str(response.get("filled_quantity", 0))),
                "remaining_quantity": Decimal(str(response.get("remaining_quantity", 0))),
                "average_price": Decimal(str(response.get("avg_price", 0))),
                "updated_at": datetime.now()
            }
        except Exception as e:
            raise Exception(f"Failed to get order status: {str(e)}")

    async def get_balance(self, asset: str) -> Dict[str, Any]:
        """Get balance for a specific asset"""
        try:
            response = await self._make_request(
                "POST",
                "/exchange/v1/users/balances",
                authenticated=True
            )

            # Find the asset in the response
            for balance in response:
                if balance.get("currency") == asset:
                    return {
                        "asset": asset,
                        "free": Decimal(str(balance.get("balance", 0))),
                        "locked": Decimal(str(balance.get("locked_balance", 0))),
                        "total": Decimal(str(balance.get("balance", 0)))
                    }

            return {"asset": asset, "free": Decimal("0"), "locked": Decimal("0"), "total": Decimal("0")}
        except Exception as e:
            raise Exception(f"Failed to get balance: {str(e)}")

    async def get_market_price(self, ticker: str) -> Decimal:
        """Get current market price"""
        market = self.format_ticker(ticker)
        try:
            response = await self._make_request(
                "GET",
                "/exchange/ticker"
            )

            # Find the market in the response
            for item in response:
                if item.get("market") == market:
                    return Decimal(str(item.get("last_price", 0)))

            raise Exception(f"Market {market} not found")
        except Exception as e:
            raise Exception(f"Failed to get market price: {str(e)}")

    async def get_ticker_info(self, ticker: str) -> Dict[str, Any]:
        """Get ticker information"""
        market = self.format_ticker(ticker)
        try:
            response = await self._make_request(
                "GET",
                "/exchange/v1/markets_details"
            )

            # Find the market
            for market_info in response:
                if market_info.get("symbol") == market:
                    return {
                        "symbol": ticker,
                        "min_quantity": Decimal(str(market_info.get("min_quantity", 0))),
                        "max_quantity": Decimal(str(market_info.get("max_quantity", 999999))),
                        "price_precision": int(market_info.get("price_precision", 2)),
                        "quantity_precision": int(market_info.get("quantity_precision", 8)),
                        "min_notional": Decimal(str(market_info.get("min_notional", 0)))
                    }

            raise Exception(f"Market info for {market} not found")
        except Exception as e:
            raise Exception(f"Failed to get ticker info: {str(e)}")

    def format_ticker(self, ticker: str) -> str:
        """Format ticker to CoinDCX format (ETH/USDT -> B-ETH_USDT for futures)"""
        # Remove slash and add B- prefix for futures
        base_ticker = ticker.replace('/', '_')
        return f"B-{base_ticker}"  # B- prefix indicates futures

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Register the adapter with the factory
from app.exchanges.factory import ExchangeFactory
ExchangeFactory.register('coindcx', CoinDCXAdapter)
ExchangeFactory.register('coindcx_f', CoinDCXAdapter)
