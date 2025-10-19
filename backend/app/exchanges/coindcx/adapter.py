"""
CoinDCX Futures Exchange Adapter
Wraps the CoinDCX Futures client to implement BaseExchange interface
"""

from typing import Dict, List, Optional
from app.exchanges.base import (
    BaseExchange,
    OrderRequest,
    OrderResponse,
    Position,
    OrderSide,
    OrderType,
    OrderStatus
)
from app.exchanges import ExchangeRegistry
from app.exchanges.coindcx.client import CoinDCXFutures
from app.exchanges.coindcx.utils import get_current_price, find_position_leverage
import logging

logger = logging.getLogger(__name__)


@ExchangeRegistry.register("coindcx", "coindcx_futures", "CoinDCX F")
class CoinDCXAdapter(BaseExchange):
    """Adapter for CoinDCX Futures exchange"""

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        super().__init__(api_key, api_secret, testnet)
        # Initialize the CoinDCX client
        self.client = CoinDCXFutures(api_key=api_key, secret_key=api_secret)

        # CoinDCX order type mapping
        self._order_type_mapping = {
            OrderType.MARKET: "market_order",
            OrderType.LIMIT: "limit_order",
            OrderType.STOP_LOSS: "stop_market",
            OrderType.TAKE_PROFIT: "take_profit_market"
        }

        logger.info(f"CoinDCX Futures adapter initialized (testnet={testnet})")

    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place order on CoinDCX Futures"""
        try:
            # Normalize symbol to CoinDCX format
            coindcx_symbol = self.normalize_symbol(order.symbol)

            # Map order type
            coindcx_order_type = self._order_type_mapping.get(order.order_type, "limit_order")

            logger.info(
                f"Placing {order.side.value} order: {coindcx_symbol} "
                f"qty={order.quantity} price={order.price}"
            )

            # Place order using CoinDCX client
            result = self.client.place_order(
                pair=coindcx_symbol,
                side=order.side.value,
                order_type=coindcx_order_type,
                quantity=order.quantity,
                leverage=order.leverage or 1,
                price=order.price,
                margin_currency="INR"
            )

            # CoinDCX returns a list of orders, extract the first one
            order_data = result[0] if isinstance(result, list) else result

            # Convert response to standard format
            order_response = OrderResponse(
                order_id=order_data['id'],
                symbol=order.symbol,
                side=order.side,
                status=self._map_status(order_data.get('status', 'open')),
                order_type=order.order_type,
                quantity=order.quantity,
                filled_quantity=float(order_data.get('filled_quantity', 0.0)),
                price=order.price,
                average_price=float(order_data['avg_price']) if order_data.get('avg_price') else None,
                timestamp=order_data.get('created_at', ''),
                exchange_specific=order_data
            )

            logger.info(f"Order placed successfully: {order_response.order_id}")
            return order_response

        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            raise

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel order on CoinDCX"""
        try:
            self.client.cancel_order(order_id)
            logger.info(f"Order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False

    async def get_order(self, order_id: str, symbol: str) -> OrderResponse:
        """Get order details"""
        try:
            # CoinDCX doesn't have a direct get_order endpoint
            # Fetch recent orders and find the matching one
            orders = self.client.get_orders(status="all", size=100)

            for order_data in orders:
                if order_data['id'] == order_id:
                    return self._convert_order_response(order_data)

            raise ValueError(f"Order {order_id} not found")

        except Exception as e:
            logger.error(f"Failed to get order {order_id}: {e}")
            raise

    async def get_open_orders(self, symbol: Optional[str] = None) -> List[OrderResponse]:
        """Get all open orders"""
        try:
            orders = self.client.get_orders(status="open", size=100)

            result = []
            for order_data in orders:
                order_symbol = self.denormalize_symbol(order_data['pair'])
                if symbol is None or order_symbol == symbol:
                    result.append(self._convert_order_response(order_data))

            logger.info(f"Found {len(result)} open orders")
            return result

        except Exception as e:
            logger.error(f"Failed to get open orders: {e}")
            return []

    async def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a symbol"""
        try:
            coindcx_symbol = self.normalize_symbol(symbol)
            positions = self.client.get_positions(size=100)

            for pos in positions:
                if pos.pair == coindcx_symbol and pos.active_pos != 0:
                    # Get current price
                    current_price = await self.get_current_price(symbol)

                    # Calculate unrealized PnL
                    unrealized_pnl = (current_price - pos.avg_price) * pos.active_pos

                    return Position(
                        symbol=symbol,
                        size=pos.active_pos,
                        entry_price=pos.avg_price,
                        current_price=current_price,
                        unrealized_pnl=unrealized_pnl,
                        realized_pnl=0.0,  # CoinDCX doesn't provide this directly
                        leverage=find_position_leverage(self.client, coindcx_symbol),
                        liquidation_price=pos.liquidation_price
                    )

            return None

        except Exception as e:
            logger.error(f"Failed to get position for {symbol}: {e}")
            return None

    async def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        # CoinDCX Futures uses INR wallet
        # This would need to be implemented based on their wallet API
        # For now, return empty dict
        logger.warning("get_balance() not fully implemented for CoinDCX")
        return {"INR": 0.0}

    async def get_current_price(self, symbol: str) -> float:
        """Get current market price"""
        try:
            coindcx_symbol = self.normalize_symbol(symbol)
            price = get_current_price(self.client, coindcx_symbol)
            return price
        except Exception as e:
            logger.error(f"Failed to get current price for {symbol}: {e}")
            raise

    def normalize_symbol(self, symbol: str) -> str:
        """
        Convert standard format to CoinDCX format
        ETH/USDT -> B-ETH_USDT
        """
        if '/' in symbol:
            base, quote = symbol.split('/')
            return f"B-{base}_{quote}"
        return symbol

    def denormalize_symbol(self, exchange_symbol: str) -> str:
        """
        Convert CoinDCX format to standard format
        B-ETH_USDT -> ETH/USDT
        """
        if exchange_symbol.startswith('B-'):
            parts = exchange_symbol[2:].split('_')
            return f"{parts[0]}/{parts[1]}"
        return exchange_symbol

    def _map_status(self, coindcx_status: str) -> OrderStatus:
        """Map CoinDCX status to standard OrderStatus"""
        mapping = {
            'open': OrderStatus.OPEN,
            'filled': OrderStatus.FILLED,
            'cancelled': OrderStatus.CANCELLED,
            'rejected': OrderStatus.REJECTED,
            'untriggered': OrderStatus.OPEN,
            'initial': OrderStatus.OPEN
        }
        return mapping.get(coindcx_status.lower(), OrderStatus.OPEN)

    def _convert_order_response(self, order_data: Dict) -> OrderResponse:
        """Convert CoinDCX order to standard OrderResponse"""
        return OrderResponse(
            order_id=order_data['id'],
            symbol=self.denormalize_symbol(order_data['pair']),
            side=OrderSide.BUY if order_data['side'] == 'buy' else OrderSide.SELL,
            status=self._map_status(order_data.get('status', 'open')),
            order_type=OrderType.LIMIT,  # Determine from order_data if needed
            quantity=float(order_data.get('total_quantity', 0.0)),
            filled_quantity=float(order_data.get('filled_quantity', 0.0)),
            price=float(order_data['price']) if order_data.get('price') else None,
            average_price=float(order_data['avg_price']) if order_data.get('avg_price') else None,
            timestamp=order_data.get('created_at', ''),
            exchange_specific=order_data
        )


# Export the adapter
__all__ = ['CoinDCXAdapter']
