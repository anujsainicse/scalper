# Exchange Integration - Bot Start/Stop with Live Orders

## Overview

The bot start and stop endpoints now integrate with live exchanges (CoinDCX) to automatically place and cancel orders.

## What Was Changed

### 1. **Start Endpoint** (`POST /api/v1/bots/{bot_id}/start`)

**New Behavior:**
- ✅ Creates exchange adapter (CoinDCX or Binance)
- ✅ Places LIMIT order on exchange based on `first_order` field
  - If `first_order = "BUY"`: Places buy at `buy_price`
  - If `first_order = "SELL"`: Places sell at `sell_price`
- ✅ Saves order to database with exchange order ID
- ✅ Sets bot status to `ACTIVE`
- ✅ Creates activity log with order details
- ✅ Sends Telegram notification with order info

**Error Handling:**
- If order placement fails:
  - Bot status set to `ERROR` (not `ACTIVE`)
  - Error logged in activity logs
  - Returns HTTP 500 with error details
  - No order record created in database

### 2. **Stop Endpoint** (`POST /api/v1/bots/{bot_id}/stop`)

**New Behavior:**
- ✅ Queries all PENDING orders for the bot
- ✅ Cancels each order on the exchange
- ✅ Updates order status to `CANCELLED` in database
- ✅ Sets bot status to `STOPPED`
- ✅ Logs cancellation results
- ✅ Sends Telegram notification with cancellation count

**Error Handling:**
- Failed cancellations are logged but don't block stopping
- Bot still transitions to `STOPPED` even if some orders fail to cancel
- Activity log shows success/failure count

### 3. **Helper Function**

`get_exchange_for_bot(bot: Bot) -> BaseExchange`
- Maps bot exchange to adapter name
- Uses `ExchangeFactory.create_sync()` to initialize
- Loads API credentials from environment variables
- Supports CoinDCX and Binance (extensible)

## Code Changes

**File:** `backend/app/api/v1/endpoints/bots.py`

### Added Imports
```python
import logging
from app.models.order import Order as OrderModel, OrderStatus as DBOrderStatus, OrderType as DBOrderType
from app.exchanges import ExchangeFactory, OrderRequest, OrderSide, OrderType, BaseExchange
```

### Exchange Helper
```python
def get_exchange_for_bot(bot: Bot) -> BaseExchange:
    exchange_map = {
        "CoinDCX F": "coindcx",
        "Binance": "binance",
    }
    exchange_name = exchange_map.get(bot.exchange.value)
    return ExchangeFactory.create_sync(exchange_name)
```

### Modified Endpoints
- `start_bot()` - 117 lines (was 29 lines)
- `stop_bot()` - 104 lines (was 32 lines)

## Environment Setup

### Required Environment Variables

Add to `backend/.env`:

```env
# CoinDCX Futures
COINDCX_API_KEY=your-coindcx-api-key
COINDCX_API_SECRET=your-coindcx-secret-key
COINDCX_TESTNET=false

# Binance (if using)
BINANCE_API_KEY=your-binance-api-key
BINANCE_API_SECRET=your-binance-secret-key
BINANCE_TESTNET=true
```

### Get CoinDCX API Keys

1. Go to https://coindcx.com/
2. Login → Settings → API Management
3. Create new API key with trading permissions
4. Copy API Key and Secret Key
5. Add to `.env` file

**⚠️ IMPORTANT**: Start with testnet or small amounts for testing!

## Testing

### 1. **Verify Exchange Configuration**

```bash
cd backend
source venv/bin/activate
python -c "from app.core.exchange_config import get_exchange_config; print(get_exchange_config('coindcx'))"
```

Should output your API configuration (without showing secrets).

### 2. **Test Start Endpoint**

**Create a bot via UI:**
- Ticker: ETH/USDT
- Exchange: CoinDCX F
- First Order: BUY
- Quantity: 0.01
- Buy Price: (2% below current LTP)
- Sell Price: (2% above current LTP)

**Click "Start"** - This will:
1. Call `POST /api/v1/bots/{bot_id}/start`
2. Place a LIMIT BUY order on CoinDCX
3. Show order ID in activity log
4. Send Telegram notification

**Verify:**
- Check activity log: "Bot started and BUY order placed at $X"
- Check Orders tab: New order with status PENDING
- Check CoinDCX: Order appears in open orders
- Check Telegram: Notification with order details

### 3. **Test Stop Endpoint**

**Click "Stop"** on an active bot with pending orders:

**Verify:**
- Activity log: "Bot stopped and X pending order(s) cancelled"
- Orders tab: Order status changed to CANCELLED
- CoinDCX: Order no longer in open orders
- Telegram: Notification with cancellation count

### 4. **Test Error Scenarios**

**Invalid Credentials:**
```bash
# Set wrong API key in .env
COINDCX_API_KEY=invalid-key
```

Start a bot → Should fail with:
- Bot status: ERROR
- Activity log: "Failed to place order: ..."
- HTTP 500 response

**Insufficient Balance:**
- Try to place large order
- Should fail with exchange error
- Bot status: ERROR

**Network Error:**
- Disconnect internet
- Try to start bot
- Should handle gracefully

## Order Flow Diagram

```
[User clicks Start]
     ↓
[GET bot from database]
     ↓
[Create exchange adapter]
     ↓
[Prepare OrderRequest]
     ↓
[exchange.place_order()] ─→ [CoinDCX API]
     ↓                              ↓
[Receive OrderResponse] ←─── [Returns order_id]
     ↓
[Save Order to database]
     ↓
[Set bot.status = ACTIVE]
     ↓
[Create activity log]
     ↓
[Send Telegram notification]
     ↓
[Return bot to frontend]
```

## Database Schema

### Order Record Created on Start

```sql
INSERT INTO orders (
    id,
    bot_id,
    exchange_order_id,    -- From CoinDCX response
    symbol,               -- "ETH/USDT"
    side,                 -- "BUY" or "SELL"
    order_type,           -- "LIMIT"
    quantity,             -- From bot
    price,                -- From bot (buy_price or sell_price)
    status,               -- "PENDING"
    filled_quantity,      -- 0.0 initially
    filled_price,         -- NULL initially
    commission,           -- 0.0 initially
    created_at,
    updated_at
) VALUES (...);
```

## API Response Examples

### Successful Start

**Request:**
```bash
POST /api/v1/bots/abc-123/start
```

**Response (200 OK):**
```json
{
  "id": "abc-123",
  "ticker": "ETH/USDT",
  "exchange": "CoinDCX F",
  "first_order": "BUY",
  "quantity": 0.01,
  "buy_price": 2950.00,
  "sell_price": 3050.00,
  "status": "ACTIVE",
  "pnl": 0.0,
  "total_trades": 0,
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T10:05:00Z"
}
```

**Activity Log:**
```
[SUCCESS] Bot started and BUY order placed at $2950.00
```

**Orders Table:**
```
| order_id | exchange_order_id | symbol    | side | status  | price   |
|----------|-------------------|-----------|------|---------|---------|
| def-456  | CDX-789123        | ETH/USDT  | BUY  | PENDING | 2950.00 |
```

### Failed Start (No API Credentials)

**Request:**
```bash
POST /api/v1/bots/abc-123/start
```

**Response (500 Internal Server Error):**
```json
{
  "detail": "Exchange configuration error: Missing API credentials for exchange 'coindcx'"
}
```

**Bot Status:** `ERROR`

**Activity Log:**
```
[ERROR] Failed to start bot: Missing API credentials for exchange 'coindcx'
```

### Successful Stop

**Request:**
```bash
POST /api/v1/bots/abc-123/stop
```

**Response (200 OK):**
```json
{
  "id": "abc-123",
  "status": "STOPPED",
  ...
}
```

**Activity Log:**
```
[WARNING] Bot stopped and 1 pending order(s) cancelled
```

## Monitoring & Debugging

### Check Logs

```bash
# Backend logs
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --log-level=debug
```

Look for:
```
INFO: Placing buy order for bot abc-123: ETH/USDT @ 2950.0
INFO: Order placed successfully: CDX-789123
INFO: Bot abc-123 started successfully with order CDX-789123
```

### Database Queries

```sql
-- Check orders for a bot
SELECT * FROM orders WHERE bot_id = 'abc-123' ORDER BY created_at DESC;

-- Check pending orders
SELECT * FROM orders WHERE status = 'PENDING';

-- Check activity logs
SELECT * FROM activity_logs WHERE bot_id = 'abc-123' ORDER BY timestamp DESC LIMIT 10;
```

### Exchange API Logs

Check CoinDCX order history:
1. Login to CoinDCX
2. Go to Orders → Order History
3. Verify order appears with correct details

## Troubleshooting

### Issue: "Exchange configuration error"

**Solution:**
- Check `.env` file has correct API keys
- Verify environment variables are loaded: `echo $COINDCX_API_KEY`
- Restart backend server after changing `.env`

### Issue: "Failed to place order: insufficient balance"

**Solution:**
- Check account balance on CoinDCX
- Reduce order quantity
- Add funds to account

### Issue: "Order placed but not saved to database"

**Solution:**
- Check database connection
- Check `orders` table exists: `\d orders` in psql
- Run migration: `alembic upgrade head`

### Issue: "Bot stuck in ACTIVE with no orders"

**Solution:**
```sql
-- Reset bot status manually
UPDATE bots SET status = 'STOPPED' WHERE id = 'abc-123';
```

## Security Notes

- ✅ API credentials stored in environment variables (not code)
- ✅ Credentials never logged or sent to frontend
- ✅ Exchange requests use HTTPS
- ✅ Errors don't expose sensitive data
- ⚠️ Keep `.env` file secure (never commit to git)
- ⚠️ Use separate API keys for testnet/production

## Next Steps

1. **Test thoroughly** with small amounts
2. **Monitor** activity logs for issues
3. **Set up** order fill webhook (future enhancement)
4. **Implement** order status polling (future enhancement)
5. **Add** position management (future enhancement)

## Support

If you encounter issues:
1. Check logs (backend console)
2. Check activity logs (UI)
3. Verify API credentials
4. Check database records
5. Review CoinDCX order history

---

**Last Updated:** January 2025
**Version:** 1.0.0
