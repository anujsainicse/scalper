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

**Last Updated**: 2025-10-19
**Maintained By**: Claude Sessions
**Purpose**: Track fixes and prevent regression
