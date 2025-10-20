"""
Test script to buy 1 ETH at $3800 on CoinDCX Futures
AUTO MODE - No confirmation required (for automated testing)
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.exchanges import ExchangeFactory, OrderRequest, OrderSide, OrderType
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_buy_eth():
    """Test buying 1 ETH at $3800 - AUTO MODE"""

    print("=" * 60)
    print("CoinDCX Futures - Buy 1 ETH at $3800 [AUTO MODE]")
    print("=" * 60)

    try:
        # Step 1: Create exchange instance
        print("\n[1/5] Creating CoinDCX Futures exchange instance...")
        exchange = await ExchangeFactory.create("coindcx")
        print(f"✅ Exchange created: {exchange}")

        # Step 2: Get current ETH price
        print("\n[2/5] Fetching current ETH/USDT price...")
        current_price = await exchange.get_current_price("ETH/USDT")
        print(f"✅ Current ETH price: ${current_price:,.2f}")

        # Step 3: Check if we have an existing position
        print("\n[3/5] Checking existing positions...")
        position = await exchange.get_position("ETH/USDT")
        if position:
            print(f"⚠️  Existing position found:")
            print(f"   Size: {position.size}")
            print(f"   Entry Price: ${position.entry_price:,.2f}")
            print(f"   Current Price: ${position.current_price:,.2f}")
            print(f"   Unrealized PnL: ${position.unrealized_pnl:,.2f}")
            print(f"   Leverage: {position.leverage}x")
            print(f"   Liquidation Price: ${position.liquidation_price:,.2f}")

            # Warn about leverage lock
            print(f"\n⚠️  WARNING: Position exists with {position.leverage}x leverage")
            print(f"   New orders MUST use {position.leverage}x leverage!")
            leverage = position.leverage
        else:
            print("✅ No existing position")
            leverage = 3  # Default to 3x for new positions

        # Step 4: Create order request
        print(f"\n[4/5] Creating BUY order for 1 ETH at $3800...")
        print(f"   Symbol: ETH/USDT")
        print(f"   Side: BUY")
        print(f"   Type: LIMIT")
        print(f"   Quantity: 1.0 ETH")
        print(f"   Price: $3,800.00")
        print(f"   Leverage: {leverage}x")

        order = OrderRequest(
            symbol="ETH/USDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=1.0,
            price=3800.0,
            leverage=leverage
        )

        # AUTO MODE - Skip confirmation
        print(f"\n{'='*60}")
        print("🤖 AUTO MODE - Placing order without confirmation")
        print(f"{'='*60}")
        print(f"Order Details:")
        print(f"  • Buy 1 ETH at $3,800.00")
        print(f"  • Leverage: {leverage}x")
        print(f"  • Current market price: ${current_price:,.2f}")

        if current_price > 3800:
            print(f"  ✅ Good deal! ${(current_price - 3800):,.2f} below market")
        else:
            print(f"  ⚠️  ${(3800 - current_price):,.2f} above market price!")

        # Step 5: Place the order
        print("\n[5/5] Placing order on CoinDCX Futures...")
        response = await exchange.place_order(order)

        print("\n" + "="*60)
        print("✅ ORDER PLACED SUCCESSFULLY!")
        print("="*60)
        print(f"Order ID: {response.order_id}")
        print(f"Symbol: {response.symbol}")
        print(f"Side: {response.side.value.upper()}")
        print(f"Status: {response.status.value.upper()}")
        print(f"Quantity: {response.quantity}")
        print(f"Price: ${response.price:,.2f}")
        print(f"Filled: {response.filled_quantity}")
        print(f"Timestamp: {response.timestamp}")

        print("\n💡 Order Details:")
        print(f"   • Order is now OPEN in the orderbook")
        print(f"   • It will be filled when ETH price reaches $3,800")
        print(f"   • You can cancel anytime before it's filled")
        print(f"   • Order ID: {response.order_id}")

        # Show how to cancel
        print("\n" + "="*60)
        print("📝 To cancel this order, run:")
        print("="*60)
        print(f"python3 cancel_order.py {response.order_id}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def show_open_orders():
    """Show all open orders"""
    print("\n" + "="*60)
    print("OPEN ORDERS")
    print("="*60)

    try:
        exchange = await ExchangeFactory.create("coindcx")
        orders = await exchange.get_open_orders("ETH/USDT")

        if not orders:
            print("No open orders for ETH/USDT")
        else:
            for i, order in enumerate(orders, 1):
                print(f"\n[{i}] Order ID: {order.order_id}")
                print(f"    Symbol: {order.symbol}")
                print(f"    Side: {order.side.value.upper()}")
                print(f"    Type: {order.order_type.value}")
                print(f"    Quantity: {order.quantity}")
                print(f"    Price: ${order.price:,.2f}")
                print(f"    Status: {order.status.value.upper()}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("\n🚀 CoinDCX Futures Test Script [AUTO MODE]")
    print("Using new exchange integration system")
    print("⚠️  WARNING: This will place REAL orders without confirmation!\n")

    # Check if API credentials are set
    if not os.getenv("COINDCX_API_KEY") or not os.getenv("COINDCX_API_SECRET"):
        print("❌ Error: CoinDCX API credentials not found!")
        print("\nPlease set the following environment variables:")
        print("  COINDCX_API_KEY=your_api_key")
        print("  COINDCX_API_SECRET=your_api_secret")
        sys.exit(1)

    # Run the test
    asyncio.run(test_buy_eth())

    # Show open orders
    asyncio.run(show_open_orders())
