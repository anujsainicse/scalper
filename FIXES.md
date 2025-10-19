# Bug Fixes & Technical Changes

This document tracks specific bug fixes and technical improvements made to the Scalper Bot Dashboard. This helps future development sessions understand what issues have been resolved and how.

---

## [2025-10-19] - Duplicate Bot Key Error Fix

### Issue
React console error: "Encountered two children with the same key" when rendering bot cards in ActiveBots component.

### Root Cause
Race condition between:
1. Manual state updates (adding/updating bots directly in the state array)
2. Automatic polling (fetching bots from server every 5 seconds via DataLoader)

This caused bots to be duplicated in the state:
- Bot created → manually added to state → polling fetches same bot → duplicate!
- Same issue occurred with `updateBotFromForm` and `toggleBot`

### Solution
Modified `store/botStore.ts` to use a **single source of truth** pattern:
- Instead of manually manipulating the bots array, always call `fetchBots()` after mutations
- This ensures the state always reflects the server's database exactly

### Files Changed
**`store/botStore.ts`** (3 functions updated):

1. **`addBot`** (lines 97-125)
   ```typescript
   // BEFORE: Manual state manipulation
   const newBot = apiToActiveBot(apiBot);
   set((state) => ({
     bots: [...state.bots, newBot],
     isLoading: false,
   }));

   // AFTER: Fetch from server
   await get().fetchBots();
   set({ isLoading: false });
   ```

2. **`updateBotFromForm`** (lines 158-189)
   ```typescript
   // BEFORE: Manual update
   const updatedBot = apiToActiveBot(apiBot);
   set((state) => ({
     bots: state.bots.map((b) => b.id === botId ? updatedBot : b),
     editingBotId: null,
     isLoading: false,
   }));

   // AFTER: Fetch from server
   await get().fetchBots();
   set({
     editingBotId: null,
     isLoading: false,
   });
   ```

3. **`toggleBot`** (lines 197-216)
   ```typescript
   // BEFORE: Manual update
   const updatedBot = apiToActiveBot(apiBot);
   set((state) => ({
     bots: state.bots.map((b) => b.id === botId ? updatedBot : b),
     isLoading: false,
   }));

   // AFTER: Fetch from server
   await get().fetchBots();
   set({ isLoading: false });
   ```

### Benefits
- ✅ No more duplicate bot errors
- ✅ State always in sync with database
- ✅ Simpler state management logic
- ✅ Prevents future race conditions
- ✅ More reliable polling behavior

---

## [2025-10-19] - Delete Bot False Error Fix

### Issue
When deleting a bot:
- Operation succeeded (bot was deleted)
- Toast showed "Failed to delete bot" error
- Deletion took ~2 seconds

### Root Cause
Backend DELETE endpoint returns **HTTP 204 No Content** with empty response body.
Frontend API client tried to parse empty response as JSON:
```typescript
return response.json(); // ❌ Throws error on empty body
```

### Solution
Added check for 204 No Content responses in API client.

### Files Changed
**`lib/api.ts`** (lines 85-88):
```typescript
// Handle 204 No Content responses (no body to parse)
if (response.status === 204 || response.headers.get('content-length') === '0') {
  return null as T;
}

return response.json();
```

### Notes
- Slow deletion (~2 seconds) is expected behavior:
  - Backend sends Telegram notification (network call)
  - Frontend fetches all logs after deletion
  - This ensures proper notification delivery and log updates

---

## [2025-10-19] - Redis LTP Integration & Enhanced Price Controls

### Changes Made

#### Backend: Redis Price Endpoint
Added new endpoint to fetch Last Traded Price (LTP) data from Redis.

**Files Added:**
- `backend/app/api/v1/endpoints/price.py` - Price endpoint
- `backend/app/core/redis.py` - Redis client with async support

**Files Modified:**
- `backend/app/api/v1/router.py` - Added price router

**Endpoint Details:**
- `GET /api/v1/price/ltp?exchange={exchange}&ticker={ticker}`
- Supports: CoinDCX F, Binance, Delta, Bybit
- Returns: LTP, funding rate, timestamp, etc.
- Redis key format: `{exchange_prefix}:{base_symbol}`
  - Example: `coindcx_futures:ETH`

#### Frontend: Real-time Price Display & Controls

**`components/BotConfiguration.tsx`** - Major enhancements:

1. **Real-time LTP Display**
   - Fetches price data when ticker/exchange changes
   - Displays current price in header
   - Shows loading state while fetching

2. **Percentage-based Price Buttons**
   - Buy Price: -1%, -0.5%, -0.1%, +0.1%, +0.5%, +1%
   - Sell Price: -1%, -0.5%, -0.1%, +0.1%, +0.5%, +1%
   - Uses multipliers (0.999, 1.001, etc.)

3. **Dynamic Decimal Precision**
   - Matches LTP decimal places
   - Auto-adjusts quantity, buy price, sell price inputs
   - Step attribute updates dynamically

4. **Auto-calculated Default Prices**
   - Buy Price = LTP × 0.98 (2% below)
   - Sell Price = LTP × 1.02 (2% above)
   - Updates on ticker/exchange change

5. **Quantity Increment Buttons**
   - Buttons: -10, -5, -2, -1, +1, +2, +5, +10
   - Color-coded (red for decrease, green for increase)

**`lib/api.ts`** - Added getLTPData method:
```typescript
async getLTPData(exchange: string, ticker: string): Promise<{
  success: boolean;
  data?: Record<string, any>;
  // ... other fields
}>
```

### User Experience Improvements
- ✅ See live prices before creating bots
- ✅ Quick price adjustments with percentage buttons
- ✅ Automatic precision matching prevents invalid decimals
- ✅ Smart defaults (±2%) save time
- ✅ Visual feedback with color-coded buttons

---

## [2025-10-19] - Dashboard Title Update

### Change
Updated main dashboard title for cleaner, modern look.

### Files Changed
**`app/page.tsx`** (line 16):
```typescript
// BEFORE
<h1 className="text-3xl md:text-4xl font-bold mb-2">
  Scalper Bot Dashboard
</h1>

// AFTER
<h1 className="text-3xl md:text-4xl font-bold mb-2">
  ⚡ Scalper
</h1>
```

### Rationale
- Lightning bolt ⚡ represents speed and quick scalping trades
- Shorter, more impactful title
- Cleaner header design

---

## Important Notes for Future Sessions

### State Management Pattern
**ALWAYS** use `fetchBots()` after mutations instead of manual state updates:
```typescript
// ✅ CORRECT
await api.createBot(data);
await get().fetchBots();

// ❌ WRONG (causes duplicates)
const newBot = apiToActiveBot(await api.createBot(data));
set((state) => ({ bots: [...state.bots, newBot] }));
```

### API Response Handling
Check for empty responses (204 No Content) before parsing JSON:
```typescript
if (response.status === 204 || response.headers.get('content-length') === '0') {
  return null as T;
}
return response.json();
```

### Polling Behavior
- DataLoader polls every 5 seconds via `fetchBots()` and `fetchLogs()`
- All mutations should work WITH the polling, not against it
- Single source of truth: server database via API

### Price Precision
- Always match LTP decimal places for quantity/prices
- Use `getDecimalPlaces()` and `roundToDecimalPlaces()` helpers
- Update input `step` attributes dynamically

### Redis Integration
- LTP data stored in Redis by external service
- Format: `{exchange_prefix}:{base_symbol}`
- Access via `/api/v1/price/ltp` endpoint
- Supports multiple exchanges

---

## Testing Checklist

After making changes, verify:
- [ ] No duplicate bot key errors in console
- [ ] Bot CRUD operations work correctly
- [ ] Delete operation shows success toast
- [ ] LTP displays correctly for all tickers
- [ ] Price buttons work with correct percentages
- [ ] Decimal precision matches LTP
- [ ] Form reset maintains calculated prices
- [ ] No race conditions during polling
- [ ] All toast notifications are accurate

---

---

## [2025-10-19] - Exchange Integration Architecture (Phase 1 & 2)

### Overview
Implemented plugin/adapter architecture for exchange-specific order execution. This foundation enables scalable integration with multiple cryptocurrency exchanges.

### Architecture Components Created

#### 1. Base Exchange Adapter (`backend/app/exchanges/base.py`)
Abstract interface defining standard methods all exchanges must implement:
- `place_order()` - Execute buy/sell orders
- `cancel_order()` - Cancel active orders
- `get_order_status()` - Track order execution
- `get_balance()` - Check account balances
- `get_market_price()` - Fetch current prices
- `get_ticker_info()` - Market specifications
- `validate_credentials()` - Test API keys

**Order Types**: MARKET, LIMIT, STOP_LOSS, TAKE_PROFIT, TAKE_PROFIT_LIMIT
**Order Status**: PENDING, OPEN, PARTIALLY_FILLED, FILLED, CANCELLED, REJECTED, EXPIRED, FAILED

#### 2. Exchange Factory (`backend/app/exchanges/factory.py`)
Registry-based pattern for dynamic adapter instantiation:
```python
from app.exchanges import ExchangeFactory, create_exchange_adapter

# Create adapter
adapter = create_exchange_adapter(
    exchange_name='coindcx',
    api_key='your-api-key',
    secret_key='your-secret',
    testnet=True
)

# Or use factory directly
adapter = ExchangeFactory.create('coindcx', api_key, secret_key)
```

#### 3. Encryption Utilities (`backend/app/utils/encryption.py`)
Fernet symmetric encryption for secure API key storage:
```python
from app.utils import encrypt_api_key, decrypt_api_key

# Encrypt before storing
encrypted = encrypt_api_key("my-api-key")

# Decrypt when needed
decrypted = decrypt_api_key(encrypted)
```

Uses `SECRET_KEY` from settings to derive encryption key consistently.

#### 4. Database Models

**ExchangeCredentials** (`backend/app/models/credentials.py`):
Stores encrypted exchange API credentials:
- `exchange`: Exchange name (e.g., 'coindcx', 'bybit')
- `api_key_encrypted`: Encrypted API key
- `secret_key_encrypted`: Encrypted secret key
- `is_testnet`: Testnet/mainnet flag
- `is_validated`: Credential validation status
- `extra_config`: JSON field for exchange-specific settings

**Order** (`backend/app/models/order.py`):
Complete order lifecycle tracking:
- Order details: ticker, side, type, quantity, price
- Status tracking through lifecycle
- Fill tracking: filled_quantity, average_fill_price
- Financial: commission, PnL
- Timestamps: created, sent_to_exchange, first_fill, last_fill, completed
- Properties: `is_complete`, `fill_percentage`

#### 5. CoinDCX Adapter (`backend/app/exchanges/coindcx/adapter.py`)
Working implementation for CoinDCX Futures:
- HMAC-SHA256 authentication
- All BaseExchangeAdapter methods implemented
- Ticker formatting for futures (ETH/USDT → B-ETH_USDT)
- Auto-registration with ExchangeFactory

**Key Features**:
- Async HTTP client (httpx)
- Signature generation for authenticated requests
- Status mapping to standard enums
- Error handling and validation

### Usage Examples

#### Creating Exchange Adapter
```python
from app.exchanges import create_exchange_adapter
from app.utils import decrypt_api_key

# Get credentials from database
creds = await get_credentials_from_db('coindcx')
api_key = decrypt_api_key(creds.api_key_encrypted)
secret_key = decrypt_api_key(creds.secret_key_encrypted)

# Create adapter
adapter = create_exchange_adapter(
    'coindcx',
    api_key,
    secret_key,
    testnet=creds.is_testnet
)

# Validate credentials
if await adapter.validate_credentials():
    print("Credentials valid!")
```

#### Placing Orders
```python
from decimal import Decimal
from app.exchanges.base import OrderSide, OrderType

# Place limit buy order
result = await adapter.place_order(
    ticker='ETH/USDT',
    side=OrderSide.BUY,
    quantity=Decimal('0.1'),
    order_type=OrderType.LIMIT,
    price=Decimal('2000.50')
)

print(f"Order ID: {result['order_id']}")
print(f"Status: {result['status']}")
```

#### Checking Order Status
```python
status = await adapter.get_order_status(
    order_id='abc123',
    ticker='ETH/USDT'
)

print(f"Filled: {status['filled_quantity']}")
print(f"Status: {status['status']}")
```

### File Structure
```
backend/app/
├── exchanges/
│   ├── __init__.py
│   ├── base.py                    # BaseExchangeAdapter
│   ├── factory.py                 # ExchangeFactory
│   ├── coindcx/
│   │   ├── __init__.py
│   │   └── adapter.py             # CoinDCXAdapter
│   └── bybit/
│       └── __init__.py            # Placeholder
├── models/
│   ├── bot.py                     # Updated Exchange enum
│   ├── credentials.py             # ExchangeCredentials model
│   └── order.py                   # Order model
└── utils/
    ├── __init__.py
    └── encryption.py              # Encryption utilities
```

### Database Schema

#### exchange_credentials
```sql
CREATE TABLE exchange_credentials (
    id UUID PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    exchange_display_name VARCHAR(100) NOT NULL,
    api_key_encrypted VARCHAR(500) NOT NULL,
    secret_key_encrypted VARCHAR(500) NOT NULL,
    passphrase_encrypted VARCHAR(500),
    is_testnet BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    label VARCHAR(100),
    description VARCHAR(500),
    is_validated BOOLEAN DEFAULT FALSE,
    last_validated_at TIMESTAMP WITH TIME ZONE,
    validation_error VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    extra_config JSON
);
```

#### orders
```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    bot_id UUID REFERENCES bots(id) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    exchange_order_id VARCHAR(100),
    ticker VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    quantity FLOAT NOT NULL,
    filled_quantity FLOAT DEFAULT 0,
    remaining_quantity FLOAT,
    price FLOAT,
    average_fill_price FLOAT,
    stop_price FLOAT,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    commission FLOAT DEFAULT 0,
    commission_asset VARCHAR(20),
    quote_quantity FLOAT,
    pnl FLOAT,
    error_message VARCHAR(500),
    retry_count FLOAT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sent_to_exchange_at TIMESTAMP WITH TIME ZONE,
    first_fill_at TIMESTAMP WITH TIME ZONE,
    last_fill_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    extra_data JSON
);
```

### Next Steps for Full Integration

#### Phase 3: Trading Service Layer
- Create `TradingService` to orchestrate bot execution
- Implement `OrderManager` for order lifecycle
- Add `RiskManager` for pre-trade validation
- Integrate with bot start/stop endpoints

#### Phase 4: API Endpoints
- `/api/v1/credentials` - CRUD for exchange credentials
- `/api/v1/orders` - Order history and tracking
- Update `/api/v1/bots` to trigger trading

#### Phase 5: Background Workers
- Celery workers for bot execution
- Price monitoring tasks
- Order fill detection
- PnL calculation

#### Phase 6: Frontend Integration
- Exchange credentials management UI
- Order history display
- Real-time order status updates
- Trade execution visualization

### Adding New Exchanges

To add a new exchange (e.g., Binance):

1. **Create adapter directory**:
```bash
mkdir backend/app/exchanges/binance
```

2. **Implement adapter**:
```python
# backend/app/exchanges/binance/adapter.py
from app.exchanges.base import BaseExchangeAdapter

class BinanceAdapter(BaseExchangeAdapter):
    @property
    def exchange_name(self) -> str:
        return "binance"

    # Implement all abstract methods...
```

3. **Register with factory**:
```python
from app.exchanges.factory import ExchangeFactory
ExchangeFactory.register('binance', BinanceAdapter)
```

4. **Update Exchange enum**:
```python
# backend/app/models/bot.py
class Exchange(str, enum.Enum):
    BINANCE = "Binance"
    # ... other exchanges
```

### Testing

```python
# Test adapter creation
adapter = create_exchange_adapter('coindcx', 'key', 'secret')
assert adapter.exchange_name == 'coindcx'

# Test credentials
assert await adapter.validate_credentials()

# Test order placement
result = await adapter.place_order(...)
assert result['order_id'] is not None
```

### Security Best Practices

1. **Never log decrypted keys**: Always use encrypted values in logs
2. **Rotate SECRET_KEY carefully**: Re-encrypt all credentials if changed
3. **Use testnet first**: Always test with testnet before mainnet
4. **Validate credentials**: Check API keys before storing
5. **Rate limiting**: Implement exchange-specific rate limits
6. **Error handling**: Gracefully handle API errors

### Known Limitations

1. **CoinDCX adapter**: Uses basic HTTP client, can be replaced with official library
2. **No WebSocket**: Currently polling-based, WebSocket support pending
3. **No order book**: Basic market data only
4. **Single user**: Multi-user credential management pending
5. **No position tracking**: Futures position management not implemented

### Dependencies Required

Add to `requirements.txt`:
```
httpx>=0.26.0          # HTTP client for exchange APIs
cryptography>=41.0.0   # For Fernet encryption
```

---

**Last Updated**: 2025-10-19
**Maintained By**: Claude Sessions
**Purpose**: Track fixes and prevent regression
