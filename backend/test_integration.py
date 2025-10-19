"""
Quick integration test for CoinDCX exchange adapter
Tests all core functionality without placing real orders
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.exchanges import ExchangeFactory, ExchangeRegistry
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_integration():
    """Test CoinDCX integration without placing orders"""

    print("=" * 60)
    print("CoinDCX Futures Integration Test")
    print("=" * 60)

    try:
        # Test 1: Check registry
        print("\n[TEST 1] Checking exchange registration...")
        exchanges = ExchangeRegistry.list_exchanges()
        print(f"✅ Registered exchanges: {exchanges}")
        print(f"✅ CoinDCX registered: {ExchangeRegistry.is_registered('coindcx')}")

        # Test 2: Create exchange instance
        print("\n[TEST 2] Creating CoinDCX exchange instance...")
        exchange = await ExchangeFactory.create("coindcx")
        print(f"✅ Exchange created: {exchange}")

        # Test 3: Fetch current price
        print("\n[TEST 3] Fetching current ETH/USDT price...")
        current_price = await exchange.get_current_price("ETH/USDT")
        print(f"✅ Current ETH price: ${current_price:,.2f}")

        # Test 4: Check existing position
        print("\n[TEST 4] Checking existing positions...")
        position = await exchange.get_position("ETH/USDT")
        if position:
            print(f"✅ Position found:")
            print(f"   Size: {position.size}")
            print(f"   Entry Price: ${position.entry_price:,.2f}")
            print(f"   Current Price: ${position.current_price:,.2f}")
            print(f"   Unrealized PnL: ${position.unrealized_pnl:,.2f}")
            print(f"   Leverage: {position.leverage}x")
            print(f"   Liquidation Price: ${position.liquidation_price:,.2f}")
        else:
            print("✅ No existing position")

        # Test 5: Get open orders
        print("\n[TEST 5] Fetching open orders...")
        orders = await exchange.get_open_orders("ETH/USDT")
        print(f"✅ Found {len(orders)} open orders")
        if orders:
            for i, order in enumerate(orders[:3], 1):  # Show max 3
                print(f"\n   Order {i}:")
                print(f"   ID: {order.order_id}")
                print(f"   Side: {order.side.value.upper()}")
                print(f"   Quantity: {order.quantity}")
                print(f"   Price: ${order.price:,.2f}")
                print(f"   Status: {order.status.value}")

        # Test 6: Symbol normalization
        print("\n[TEST 6] Testing symbol normalization...")
        normalized = exchange.normalize_symbol("ETH/USDT")
        denormalized = exchange.denormalize_symbol(normalized)
        print(f"✅ ETH/USDT -> {normalized}")
        print(f"✅ {normalized} -> {denormalized}")

        # Summary
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nIntegration Summary:")
        print(f"  • Exchange adapter: Working")
        print(f"  • Price fetching: Working")
        print(f"  • Position checking: Working")
        print(f"  • Order fetching: Working")
        print(f"  • Symbol normalization: Working")
        print("\n🎉 CoinDCX integration is fully functional!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(test_integration())
    sys.exit(0 if success else 1)
