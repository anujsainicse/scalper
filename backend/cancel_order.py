"""
Quick script to cancel an order by ID
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.exchanges import ExchangeFactory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def cancel_order(order_id: str):
    """Cancel an order by ID"""

    print(f"🚀 Canceling order: {order_id}")

    try:
        # Create exchange instance
        exchange = await ExchangeFactory.create("coindcx")

        # Cancel the order
        result = await exchange.cancel_order(order_id, "ETH/USDT")

        print(f"✅ Order cancelled successfully!")
        print(f"   Order ID: {result.order_id}")
        print(f"   Status: {result.status.value}")

    except Exception as e:
        print(f"❌ Error canceling order: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 cancel_order.py <order_id>")
        sys.exit(1)

    order_id = sys.argv[1]
    asyncio.run(cancel_order(order_id))
