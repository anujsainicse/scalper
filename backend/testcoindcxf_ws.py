"""
CoinDCX Futures WebSocket Test - Order Updates
Subscribes to real-time order updates via WebSocket
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import socketio

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.exchanges.coindcx.client import CoinDCXFutures
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OrderUpdateMonitor:
    """Monitor real-time order updates from CoinDCX Futures"""

    def __init__(self):
        self.client = None
        self.sio = None
        self.order_count = 0
        self.position_count = 0
        self.balance_count = 0
        self.event_count = 0

    async def on_order_update(self, data: Dict[str, Any]):
        """Handle order update events"""
        self.order_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        print(f"\n{'='*70}")
        print(f"🔔 ORDER UPDATE #{self.order_count} - {timestamp}")
        print(f"{'='*70}")

        # Parse the order data - CoinDCX sends data as a JSON string
        import json
        if isinstance(data, dict) and 'data' in data:
            # Data is a JSON string that needs parsing
            order_list = json.loads(data['data'])
            order = order_list[0] if order_list else {}
        elif isinstance(data, dict) and 'order' in data:
            order = data['order']
        else:
            order = data

        print(f"Order ID:      {order.get('id', 'N/A')}")
        print(f"Pair:          {order.get('pair', 'N/A')}")
        print(f"Side:          {order.get('side', 'N/A').upper()}")
        print(f"Status:        {order.get('status', 'N/A').upper()}")
        print(f"Order Type:    {order.get('order_type', 'N/A')}")
        print(f"Price:         ${float(order.get('price', 0)):,.2f}")
        print(f"Quantity:      {float(order.get('total_quantity', 0)):.8f}")
        print(f"Filled:        {float(order.get('filled_quantity', 0)):.8f}")
        print(f"Remaining:     {float(order.get('remaining_quantity', 0)):.8f}")
        print(f"Leverage:      {order.get('leverage', 'N/A')}x")

        # Show average fill price if available
        if order.get('avg_price'):
            avg_price = float(order.get('avg_price'))
            if avg_price > 0:
                print(f"Avg Price:     ${avg_price:,.2f}")

        # Show fee if available
        if order.get('fee_amount'):
            fee = float(order.get('fee_amount'))
            if fee > 0:
                print(f"Fee:           ${fee:.4f}")

        # Show timestamp
        if order.get('created_at'):
            print(f"Created:       {order.get('created_at')}")

        # Show display message if available
        if order.get('display_message'):
            print(f"Message:       {order.get('display_message')}")

        print(f"{'='*70}\n")

    async def on_position_update(self, data: Dict[str, Any]):
        """Handle position update events"""
        self.position_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        print(f"\n{'='*70}")
        print(f"📊 POSITION UPDATE #{self.position_count} - {timestamp}")
        print(f"{'='*70}")

        # Parse the position data - CoinDCX sends data as a JSON string
        import json
        if isinstance(data, dict) and 'data' in data:
            position_list = json.loads(data['data'])
            position = position_list[0] if position_list else {}
        elif isinstance(data, dict) and 'position' in data:
            position = data['position']
        else:
            position = data

        print(f"Position ID:       {position.get('id', 'N/A')}")
        print(f"Pair:              {position.get('pair', 'N/A')}")
        print(f"Active Position:   {float(position.get('active_pos', 0)):.8f}")
        print(f"Average Price:     ${float(position.get('avg_price', 0)):,.2f}")
        print(f"Liquidation Price: ${float(position.get('liquidation_price', 0)):,.2f}")
        print(f"Locked Margin:     ${float(position.get('locked_margin', 0)):,.2f}")

        # Show unrealized PnL if available
        if position.get('unrealized_pnl'):
            pnl = float(position.get('unrealized_pnl'))
            pnl_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
            print(f"Unrealized PnL:    {pnl_emoji} ${pnl:,.2f}")

        print(f"{'='*70}\n")

    async def on_balance_update(self, data: Dict[str, Any]):
        """Handle balance update events"""
        self.balance_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        print(f"\n{'='*70}")
        print(f"💰 BALANCE UPDATE #{self.balance_count} - {timestamp}")
        print(f"{'='*70}")

        # Parse the balance data - CoinDCX sends data as a JSON string
        import json
        if isinstance(data, dict) and 'data' in data:
            balance_list = json.loads(data['data'])
            balance = balance_list[0] if balance_list else {}
        elif isinstance(data, dict) and 'balance' in data:
            balance = data['balance']
        else:
            balance = data

        if balance.get('currency_short_name'):
            print(f"Currency:          {balance.get('currency_short_name')}")
        if balance.get('balance'):
            print(f"Available:         ${float(balance.get('balance')):,.2f}")
        if balance.get('locked_balance'):
            print(f"Locked:            ${float(balance.get('locked_balance')):,.2f}")

        print(f"{'='*70}\n")

    async def on_any_event(self, event, data):
        """Catch-all handler for debugging"""
        self.event_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        print(f"\n[{timestamp}] 🔍 Event #{self.event_count}: {event}")
        if data:
            print(f"Data: {data}")

    async def start(self):
        """Start WebSocket monitoring"""
        print("\n" + "="*70)
        print("🚀 CoinDCX Futures WebSocket Monitor (Debug Mode)")
        print("="*70)
        print("\nInitializing WebSocket client...")

        try:
            # Create CoinDCX client
            self.client = CoinDCXFutures()

            # Create SocketIO client with debugging
            self.sio = socketio.AsyncClient(
                logger=True,
                engineio_logger=True
            )

            # Register ALL event handlers BEFORE connecting
            print("\nRegistering event handlers...")

            # Specific handlers
            @self.sio.on('df-order-update')
            async def handle_order_update(data):
                await self.on_order_update(data)

            @self.sio.on('df-position-update')
            async def handle_position_update(data):
                await self.on_position_update(data)

            @self.sio.on('balance-update')
            async def handle_balance_update(data):
                await self.on_balance_update(data)

            # Catch-all handler for debugging
            @self.sio.on('*')
            async def catch_all(event, data):
                await self.on_any_event(event, data)

            # Standard SocketIO events
            @self.sio.on('connect')
            async def on_connect():
                print(f"\n✅ Connected to WebSocket!")

                # Subscribe to authenticated channel
                body = {"channel": "coindcx"}
                signature = self.client._generate_signature(body)

                print("\nSubscribing to authenticated channel...")
                await self.sio.emit('join', {
                    'channelName': 'coindcx',
                    'authSignature': signature,
                    'apiKey': self.client.api_key
                })
                print("✅ Subscription request sent!")

            @self.sio.on('disconnect')
            async def on_disconnect():
                print("\n⚠️  Disconnected from WebSocket")

            @self.sio.on('connect_error')
            async def on_connect_error(data):
                print(f"\n❌ Connection error: {data}")

            # Connect to WebSocket
            print(f"\nConnecting to {self.client.websocket_url}...")
            await self.sio.connect(
                self.client.websocket_url,
                transports=['websocket']
            )

            print("\n" + "="*70)
            print("📡 Subscribed to:")
            print("="*70)
            print("  • df-order-update (Order Updates)")
            print("  • df-position-update (Position Updates)")
            print("  • balance-update (Balance Updates)")
            print("  • * (All Events - Debug)")
            print("="*70)

            print("\n💡 Tips:")
            print("  • Place an order using: python3 testcoindcxf_auto.py")
            print("  • All WebSocket events will be shown in debug mode")
            print("  • Press Ctrl+C to stop monitoring\n")

            print("="*70)
            print("🔊 Listening for ALL WebSocket events...")
            print("="*70)

            # Start ping task
            asyncio.create_task(self._ping_task())

            # Keep the connection alive
            while True:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping monitor...")
            await self.stop()

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await self.stop()

    async def _ping_task(self):
        """Send periodic ping to keep WebSocket alive"""
        while self.sio and self.sio.connected:
            await asyncio.sleep(25)
            try:
                await self.sio.emit('ping', {'data': 'Ping message'})
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📡 Ping sent")
            except Exception as e:
                print(f"\n❌ Ping failed: {e}")
                break

    async def stop(self):
        """Stop WebSocket monitoring"""
        if self.sio and self.sio.connected:
            await self.sio.disconnect()

            # Print summary
            print("\n" + "="*70)
            print("📊 SUMMARY")
            print("="*70)
            print(f"Total Events:      {self.event_count}")
            print(f"Order Updates:     {self.order_count}")
            print(f"Position Updates:  {self.position_count}")
            print(f"Balance Updates:   {self.balance_count}")
            print("="*70)
            print("\n✅ WebSocket disconnected successfully!")


async def test_with_order_placement():
    """
    Test WebSocket monitoring with automatic order placement
    """
    print("\n" + "="*70)
    print("🧪 WebSocket Test with Order Placement")
    print("="*70)

    monitor = OrderUpdateMonitor()

    # Start monitor in background
    monitor_task = asyncio.create_task(monitor.start())

    # Wait for connection
    await asyncio.sleep(3)

    try:
        # Import exchange factory
        from app.exchanges import ExchangeFactory, OrderRequest, OrderSide, OrderType

        # Place a test order
        print("\n[TEST] Placing test order...")
        exchange = await ExchangeFactory.create("coindcx")

        order = OrderRequest(
            symbol="ETH/USDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=0.01,
            price=3500.0,
            leverage=3
        )

        response = await exchange.place_order(order)
        print(f"✅ Order placed! ID: {response.order_id}")

        # Wait for updates
        print("\n[TEST] Waiting 10 seconds for WebSocket updates...")
        await asyncio.sleep(10)

        # Cancel the order using the client directly
        print("\n[TEST] Cancelling test order...")
        cancel_client = monitor.client
        cancel_result = cancel_client.cancel_order(response.order_id)
        print(f"✅ Order cancelled! Result: {cancel_result}")

        # Wait a bit more
        await asyncio.sleep(3)

        # Stop monitor
        await monitor.stop()
        monitor_task.cancel()

    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        await monitor.stop()


if __name__ == "__main__":
    # Check API credentials
    if not os.getenv("COINDCX_API_KEY") or not os.getenv("COINDCX_API_SECRET"):
        print("\n❌ Error: CoinDCX API credentials not found!")
        print("\nPlease set the following environment variables:")
        print("  COINDCX_API_KEY=your_api_key")
        print("  COINDCX_API_SECRET=your_api_secret\n")
        sys.exit(1)

    # Get mode from command line
    mode = sys.argv[1] if len(sys.argv) > 1 else "monitor"

    if mode == "test":
        # Test mode: place order and monitor
        asyncio.run(test_with_order_placement())
    elif mode == "monitor":
        # Monitor mode: just listen for updates
        monitor = OrderUpdateMonitor()
        asyncio.run(monitor.start())
    else:
        print(f"\n❌ Error: Unknown mode '{mode}'")
        print("\nUsage: python3 testcoindcxf_ws.py [monitor|test]")
        sys.exit(1)
