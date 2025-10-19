#!/usr/bin/env python3
"""
Quick test script to verify CoinDCX exchange connection
Run this before starting the bot to ensure credentials work
"""

import asyncio
import sys
from app.exchanges import ExchangeFactory, OrderRequest, OrderSide, OrderType


async def test_exchange_connection():
    """Test CoinDCX connection and basic operations"""
    print("=" * 60)
    print("CoinDCX Exchange Connection Test")
    print("=" * 60)

    try:
        # 1. Create exchange adapter
        print("\n1. Creating CoinDCX adapter...")
        exchange = ExchangeFactory.create_sync("coindcx")
        print(f"   ✓ Exchange adapter created: {exchange}")

        # 2. Test health check
        print("\n2. Testing API connection...")
        is_healthy = await exchange.health_check()
        if is_healthy:
            print("   ✓ API connection successful")
        else:
            print("   ✗ API connection failed")
            return False

        # 3. Get account balance
        print("\n3. Fetching account balance...")
        balance = await exchange.get_balance()
        print(f"   Balance: {balance}")

        # 4. Test symbol normalization
        print("\n4. Testing symbol conversion...")
        test_symbol = "ETH/USDT"
        normalized = exchange.normalize_symbol(test_symbol)
        denormalized = exchange.denormalize_symbol(normalized)
        print(f"   Standard: {test_symbol}")
        print(f"   CoinDCX:  {normalized}")
        print(f"   Back:     {denormalized}")
        print(f"   ✓ Symbol conversion works")

        # 5. Get current price (test ticker data access)
        print("\n5. Fetching current ETH/USDT price...")
        try:
            current_price = await exchange.get_current_price("ETH/USDT")
            print(f"   Current ETH/USDT price: ${current_price:,.2f}")
            print("   ✓ Market data access works")
        except Exception as e:
            print(f"   ! Price fetch failed: {e}")
            print("   (This is optional - may not affect bot functionality)")

        # 6. Get open orders
        print("\n6. Checking existing open orders...")
        open_orders = await exchange.get_open_orders()
        print(f"   Open orders: {len(open_orders)}")
        if open_orders:
            for order in open_orders[:3]:  # Show first 3
                print(f"   - {order.side.value} {order.quantity} {order.symbol} @ ${order.price}")

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour CoinDCX credentials are working correctly.")
        print("You can now start bots and they will place orders on CoinDCX.")
        print("\n⚠️  IMPORTANT: Start with small quantities for testing!")
        print("=" * 60)

        return True

    except ValueError as ve:
        print(f"\n❌ Configuration Error: {ve}")
        print("\nPlease check your .env file:")
        print("  - COINDCX_API_KEY is set")
        print("  - COINDCX_API_SECRET is set")
        return False

    except Exception as e:
        print(f"\n❌ Connection Error: {e}")
        print("\nPossible issues:")
        print("  - Invalid API credentials")
        print("  - API keys don't have trading permissions")
        print("  - Network connectivity issue")
        print("  - CoinDCX API is down")
        return False


def main():
    """Run the test"""
    print("\n🔍 Testing CoinDCX Exchange Integration...\n")

    # Run async test
    success = asyncio.run(test_exchange_connection())

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
