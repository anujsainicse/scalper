# CoinDCX Futures WebSocket Order Monitoring

## Overview
The `testcoindcxf_ws.py` script subscribes to real-time order updates from CoinDCX Futures via WebSocket.

## Features
- ✅ Real-time order updates (df-order-update)
- ✅ Real-time position updates (df-position-update)  
- ✅ Real-time balance updates (df-balance-update)
- ✅ Debug mode to see all WebSocket events
- ✅ Automatic reconnection with ping/pong
- ✅ JSON data parsing

## Usage

### Monitor Mode (Default)
Just listen for WebSocket updates:
```bash
python3 testcoindcxf_ws.py
# OR
python3 testcoindcxf_ws.py monitor
```

### Test Mode
Automatically place and cancel a test order to see the updates:
```bash
python3 testcoindcxf_ws.py test
```

## What You'll See

### Order Updates
Every time an order changes status, you'll see:
```
======================================================================
🔔 ORDER UPDATE #1 - 22:27:46.969
======================================================================
Order ID:      789b0a3c-1e9a-4165-970f-be11b240a761
Pair:          B-ETH_USDT
Side:          BUY
Status:        INITIAL
Order Type:    limit_order
Price:         $3,500.00
Quantity:      0.01000000
Filled:        0.00000000
Remaining:     0.01000000
Leverage:      3x
Created:       1760979466991
Message:       ETH limit buy order placed!
======================================================================
```

### Position Updates
When positions change (fills, exits, etc):
```
======================================================================
📊 POSITION UPDATE #1 - 22:27:46.971
======================================================================
Position ID:       51e1209c-9f51-11f0-bd99-eb2081468b48
Pair:              B-ETH_USDT
Active Position:   0.00000000
Average Price:     $0.00
Liquidation Price: $0.00
Locked Margin:     $0.00
======================================================================
```

### Balance Updates
When your balance changes:
```
======================================================================
💰 BALANCE UPDATE #1 - 22:27:57.467
======================================================================
Currency:          INR
Available:         $1,650,841.60
Locked:            $355,112.44
======================================================================
```

## Order Status Flow

Orders typically go through these statuses:
1. `INITIAL` - Order created, being validated
2. `OPEN` - Order placed in orderbook
3. `FILLED` / `CANCELLED` - Final status

## Testing Workflow

### Terminal 1: Start Monitor
```bash
python3 testcoindcxf_ws.py monitor
```

### Terminal 2: Place Orders
```bash
python3 testcoindcxf_auto.py
```

You'll see real-time updates in Terminal 1 as the order is placed!

## Data Format

CoinDCX sends WebSocket data in this format:
```json
{
  "event": "df-order-update",
  "data": "[{\"id\":\"...\",\"status\":\"open\",...}]"
}
```

Note: The `data` field is a **JSON string** (not an object), so we parse it with `json.loads()`.

## Events Subscribed

- `df-order-update` - Order status changes
- `df-position-update` - Position changes (fills, exits, PnL)
- `df-balance-update` - Balance changes
- `*` - Catch-all for debugging (shows all events)

## Requirements

```bash
pip install python-socketio[asyncio_client] aiohttp
```

## Environment Variables

Create `.env` file:
```
COINDCX_API_KEY=your_api_key
COINDCX_API_SECRET=your_api_secret
```

## Troubleshooting

**No updates showing?**
- Make sure WebSocket connection is established (you'll see "✅ Connected to WebSocket!")
- Place an order in another terminal
- Check that your API credentials are correct

**Connection drops?**
- The script sends pings every 25 seconds to keep connection alive
- CoinDCX timeout is 20 seconds for missed pongs

**Events not parsing?**
- The script handles CoinDCX's JSON string format automatically
- Check the debug output to see raw event data

## Advanced Usage

### Custom Event Handling

You can modify the event handlers to:
- Store updates in database
- Send alerts/notifications
- Execute automated actions
- Log to file

### Subscribing to Market Data

The client also supports subscribing to:
- Price updates
- Orderbook updates
- Trade streams
- Candlestick data

See `app/exchanges/coindcx/client.py` for available subscriptions.

## Summary

This WebSocket monitor gives you real-time visibility into all order activity, which is essential for:
- Automated trading bots
- Order execution monitoring  
- Risk management
- Performance tracking
- Debugging

