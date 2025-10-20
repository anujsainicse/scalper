"""
Test script to debug bot order placement
This replicates what the bot endpoint does
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.exchanges import ExchangeFactory, OrderRequest, OrderSide, OrderType
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_bot_order_placement():
    """Test placing an order exactly like the bot endpoint does"""

    print("=" * 80)
    print("Testing Bot Order Placement (Replicating /bots/{bot_id}/start endpoint)")
    print("=" * 80)

    # Simulate bot configuration
    bot_config = {
        "ticker": "ETH/USDT",
        "exchange": "CoinDCX F",  # This is what frontend sends
        "first_order": "BUY",
        "buy_price": 3926.39,
        "sell_price": 4000.0,
        "quantity": 1.0
    }

    print("\n[1/4] Bot Configuration:")
    for key, value in bot_config.items():
        print(f"   {key}: {value}")

    try:
        # Step 1: Get exchange adapter (same as bot endpoint)
        print("\n[2/4] Getting exchange adapter...")

        # Map exchange name (same as bot endpoint does)
        exchange_map = {
            "CoinDCX F": "coindcx",
            "Binance": "binance",
        }
        exchange_name = exchange_map.get(bot_config["exchange"])
        print(f"   Exchange name: {exchange_name}")

        exchange = await ExchangeFactory.create(exchange_name)
        print(f"   ✅ Exchange: {exchange}")

        # Step 2: Create order request (EXACTLY as bot endpoint does)
        print("\n[3/4] Creating order request...")
        order_side = OrderSide.BUY if bot_config["first_order"] == "BUY" else OrderSide.SELL
        order_price = bot_config["buy_price"] if bot_config["first_order"] == "BUY" else bot_config["sell_price"]

        order_request = OrderRequest(
            symbol=bot_config["ticker"],  # "ETH/USDT"
            side=order_side,
            order_type=OrderType.LIMIT,
            quantity=float(bot_config["quantity"]),
            price=float(order_price),
            leverage=1,  # ← Bot uses 1
            time_in_force="GTC"  # ← Bot uses "GTC"
        )

        print(f"   Symbol: {order_request.symbol}")
        print(f"   Side: {order_request.side.value}")
        print(f"   Type: {order_request.order_type.value}")
        print(f"   Quantity: {order_request.quantity}")
        print(f"   Price: ${order_request.price}")
        print(f"   Leverage: {order_request.leverage}")
        print(f"   Time in Force: {order_request.time_in_force}")

        # Step 3: Place order
        print("\n[4/4] Placing order on exchange...")
        order_response = await exchange.place_order(order_request)

        print("\n" + "=" * 80)
        print("✅ ORDER PLACED SUCCESSFULLY!")
        print("=" * 80)
        print(f"Order ID: {order_response.order_id}")
        print(f"Symbol: {order_response.symbol}")
        print(f"Side: {order_response.side.value.upper()}")
        print(f"Status: {order_response.status.value.upper()}")
        print(f"Quantity: {order_response.quantity}")
        print(f"Price: ${order_response.price}")
        print(f"Timestamp: {order_response.timestamp}")

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR!")
        print("=" * 80)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")

        # Print full traceback
        import traceback
        print("\nFull Traceback:")
        traceback.print_exc()

        # Try to get more details from the error
        if hasattr(e, 'response'):
            print("\nHTTP Response Details:")
            print(f"  Status Code: {e.response.status_code}")
            print(f"  Response Text: {e.response.text}")


if __name__ == "__main__":
    asyncio.run(test_bot_order_placement())
