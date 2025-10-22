# Race Condition Fix - Bot Auto-Stop on Update

## Problem Description

When updating a bot, the bot was getting auto-stopped even though it shouldn't be. This was happening due to a **critical race condition** between the REST API and WebSocket handler.

## Root Cause

### The Sequence That Caused The Bug:

1. **User updates bot** via REST API (`PUT /api/v1/bots/{id}`)
2. **Backend cancels existing order** by calling `exchange.cancel_order()`
3. **Exchange immediately sends WebSocket cancellation event**
4. **WebSocket handler receives event** and queries database for `order.cancellation_reason`
5. **Database query returns `None`** because the transaction hasn't been committed yet
6. **WebSocket handler sees manual cancellation** and auto-stops the bot ❌
7. **REST API commits transaction** with `cancellation_reason = "UPDATE"` (too late!)

### The Race Condition:

```
Timeline of Events:

T=0  REST API: await exchange.cancel_order()
     └─> Exchange API call initiated

T=1  Exchange: Order cancelled, WebSocket event sent

T=2  WebSocket: Receives cancellation event
     └─> Queries DB: order.cancellation_reason = None (not committed yet!)
     └─> Auto-stops bot (incorrect behavior)

T=3  REST API: order.cancellation_reason = "UPDATE"
     └─> Too late! Bot already stopped.

T=4  REST API: await db.commit()
     └─> Commits "UPDATE" reason (but damage done)
```

## Solution

**Set the `cancellation_reason` and commit to database BEFORE calling the exchange API.**

### Fixed Flow:

```
Timeline of Events (FIXED):

T=0  REST API: order.cancellation_reason = "UPDATE"
T=1  REST API: order.status = CANCELLED
T=2  REST API: await db.flush()  # Commit to DB immediately!
     └─> Database now has cancellation_reason = "UPDATE"

T=3  REST API: await exchange.cancel_order()
     └─> Exchange API call initiated

T=4  Exchange: Order cancelled, WebSocket event sent

T=5  WebSocket: Receives cancellation event
     └─> Queries DB: order.cancellation_reason = "UPDATE"
     └─> Skips auto-stop (correct behavior) ✅

T=6  REST API: await db.commit()
     └─> Final commit (everything already correct)
```

## Code Changes

### Before (Incorrect Order):

```python
# Cancel order on exchange
await exchange.cancel_order(order.exchange_order_id, bot.ticker)

# Set cancellation reason (TOO LATE - WebSocket already triggered!)
order.status = DBOrderStatus.CANCELLED
order.cancellation_reason = "UPDATE"

# Commit later (TOO LATE!)
await db.commit()
```

### After (Correct Order):

```python
# Set cancellation reason FIRST
order.cancellation_reason = "UPDATE"
order.status = DBOrderStatus.CANCELLED

# Commit to database BEFORE calling exchange
await db.flush()  # ← CRITICAL: This makes it visible to WebSocket handler

# Now cancel on exchange (WebSocket will see correct reason)
await exchange.cancel_order(order.exchange_order_id, bot.ticker)

# Final commit
await db.commit()
```

## Files Modified

1. **`app/api/v1/endpoints/bots.py`**
   - `update_bot()` - Lines 302-321
   - `stop_bot()` - Lines 690-710
   - `delete_bot()` - Lines 495-522

## Key Takeaway

**When integrating REST APIs with WebSocket events, always commit critical data to the database BEFORE triggering external events that might query that same data.**

This is a common pitfall in event-driven architectures where multiple components access the same database concurrently.

## Testing

To verify the fix works:

1. Start a bot
2. Update the bot's price while it has a pending order
3. Verify:
   - Old order is cancelled
   - New order is placed
   - **Bot remains ACTIVE** (not stopped)
   - Activity log shows "Order cancelled for update operation" (not manual cancellation)

## Prevention

To prevent similar bugs in the future:

1. **Always use `db.flush()` before external API calls** that might trigger events
2. **Use database transactions properly** - commit state changes before triggering side effects
3. **Add logging** to track the order of operations
4. **Test concurrent scenarios** - WebSocket events can arrive at any time

---

**Status**: ✅ FIXED
**Date**: 2025-01-22
**Impact**: HIGH - Prevents incorrect bot auto-stop during updates
**Related Files**: `bots.py`, `websocket.py`, `order.py`
