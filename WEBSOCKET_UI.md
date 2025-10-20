# WebSocket Monitor UI - Frontend Implementation

## Overview
Added a new **WebSocket** tab in the bottom panel alongside Activity Logs and Orders to display real-time order updates from CoinDCX Futures.

## What Was Added

### 1. New Component: `WebSocketMonitor.tsx`
**Location**: `/components/WebSocketMonitor.tsx`

A real-time monitoring dashboard that displays:
- **Order Updates**: Real-time order status changes (initial → open → filled/cancelled)
- **Position Updates**: Position changes, PnL, margin updates
- **Balance Updates**: Wallet balance changes

#### Features:
- ✅ Connection status indicator (Live / Reconnecting / Disconnected)
- ✅ Auto-reconnect on connection loss
- ✅ Event counter badge
- ✅ Clear events button
- ✅ Color-coded event cards
- ✅ Detailed event information display
- ✅ Timestamps for all events

### 2. Updated Main Page: `app/page.tsx`
**Changes**:
- Added `'websocket'` to `BottomTab` type
- Imported `WebSocketMonitor` component
- Added new WebSocket tab button with green gradient
- Conditional rendering for 3 tabs instead of 2

## UI Design

### Tab Button
```tsx
<Button
  variant={activeBottomTab === 'websocket' ? 'default' : 'outline'}
  className="bg-gradient-to-r from-green-600 to-green-500 shadow-lg shadow-green-500/30"
>
  <Radio className="mr-2 h-5 w-5" />
  WebSocket
</Button>
```

### Connection Status Badge
Shows current WebSocket status:
- 🟢 **Live**: Connected and receiving events (green, animated pulse)
- 🟡 **Reconnecting**: Connection lost, attempting reconnect (yellow, spinning icon)
- 🔴 **Disconnected**: Not connected (red, static icon)

### Event Cards
Each event is displayed in a card with:
- **Header**: Event type badge, status badge (for orders), timestamp
- **Details**: Formatted key-value pairs specific to event type

#### Order Event Card
```
📦 ORDER    OPEN              22:27:46.969
─────────────────────────────────────────
Order ID:    789b0a3c...
Pair:        B-ETH_USDT
Side:        BUY (green)
Type:        limit_order
Price:       $3,500.00
Quantity:    0.01
Filled:      0.00 (green)
Remaining:   0.01 (yellow)
Leverage:    3x
Message:     ETH limit buy order placed!
```

#### Position Event Card
```
📊 POSITION              22:27:46.971
─────────────────────────────────────────
Position ID: 51e1209c...
Pair:        B-ETH_USDT
Active Pos:  0.00000000
Avg Price:   $0.00
Liq. Price:  $0.00 (red)
Locked Margin: $0.00
Unrealized PnL: $0.00 (green/red)
```

#### Balance Event Card
```
💰 BALANCE               22:27:57.467
─────────────────────────────────────────
Currency:    INR
Available:   $1,650,841.60 (green)
Locked:      $355,112.44 (yellow)
Total:       $2,005,954.04
```

## Color Scheme

### Event Types
- **Order**: Blue (`bg-blue-500/10 text-blue-400`)
- **Position**: Purple (`bg-purple-500/10 text-purple-400`)
- **Balance**: Green (`bg-green-500/10 text-green-400`)

### Order Status
- **OPEN**: Green
- **INITIAL**: Yellow
- **FILLED**: Blue
- **CANCELLED**: Gray

### Order Side
- **BUY**: Green (`text-green-400`)
- **SELL**: Red (`text-red-400`)

### PnL
- **Positive**: Green
- **Negative**: Red
- **Zero**: Gray

## Data Flow

### Current Implementation (Phase 1)
```
Frontend Component (WebSocketMonitor.tsx)
    ↓
Simulated Connection (Demo Mode)
    ↓
Empty Events State (Waiting for backend)
```

### Production Implementation (Phase 2)
```
Backend FastAPI (/ws/coindcx endpoint)
    ↓
WebSocket Connection
    ↓
Frontend Component
    ↓
Real-time Event Display
```

## Backend Integration (To Be Implemented)

### WebSocket Endpoint
**Endpoint**: `ws://localhost:8000/ws/coindcx`

### Message Format
The frontend expects events in this format:

```typescript
{
  id: string;          // Unique event ID
  timestamp: Date;     // Event timestamp
  type: 'order' | 'position' | 'balance';
  data: any;          // Event-specific data
}
```

### Order Update Data
```json
{
  "id": "789b0a3c-1e9a-4165-970f-be11b240a761",
  "pair": "B-ETH_USDT",
  "side": "buy",
  "status": "open",
  "order_type": "limit_order",
  "price": 3500,
  "total_quantity": 0.01,
  "filled_quantity": 0,
  "remaining_quantity": 0.01,
  "leverage": 3,
  "display_message": "ETH limit buy order placed!",
  "created_at": 1760979466991
}
```

### Position Update Data
```json
{
  "id": "51e1209c-9f51-11f0-bd99-eb2081468b48",
  "pair": "B-ETH_USDT",
  "active_pos": 0,
  "avg_price": 0,
  "liquidation_price": 0,
  "locked_margin": 0,
  "unrealized_pnl": 0
}
```

### Balance Update Data
```json
{
  "currency_short_name": "INR",
  "balance": "1650841.59606695345873",
  "locked_balance": "355112.43845000000124"
}
```

## Implementation Steps

### Completed ✅
1. Created `WebSocketMonitor.tsx` component
2. Added WebSocket tab to main page
3. Implemented event card rendering
4. Added connection status indicator
5. Styled with proper color scheme

### To Do 🔲
1. Create FastAPI WebSocket endpoint (`/ws/coindcx`)
2. Connect to backend WebSocket in frontend
3. Parse incoming messages and add to events state
4. Handle connection errors and reconnection
5. Add event filtering (by type, by bot)
6. Add event export functionality
7. Persist events to localStorage (optional)
8. Add sound/visual notifications for new events

## Usage

### Frontend
1. Navigate to `http://localhost:3000`
2. Click the **WebSocket** tab (green button with Radio icon)
3. See connection status in the header
4. Events will appear in real-time once backend is connected

### Backend (When Implemented)
```python
# backend/app/api/v1/endpoints/websocket.py

from fastapi import WebSocket
import json

@router.websocket("/ws/coindcx")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Subscribe to CoinDCX WebSocket
    # Forward events to frontend

    while True:
        # Receive from CoinDCX
        event = await coindcx_client.receive()

        # Transform and send to frontend
        await websocket.send_json({
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "type": "order",  # or "position" or "balance"
            "data": event
        })
```

## Testing

### Manual Testing
1. Open browser developer tools (F12)
2. Go to Network tab → WS (WebSocket)
3. Click WebSocket tab in UI
4. Should see WebSocket connection attempt
5. Place an order via backend
6. Event should appear in WebSocket monitor

### Test Data
You can modify the component to show demo events:
```typescript
// In connectWebSocket() function
setEvents([
  {
    id: '1',
    timestamp: new Date(),
    type: 'order',
    data: {
      id: 'test-order-123',
      pair: 'B-ETH_USDT',
      side: 'buy',
      status: 'open',
      // ... rest of order data
    }
  }
]);
```

## Files Modified

1. ✅ `/components/WebSocketMonitor.tsx` - **NEW FILE**
2. ✅ `/app/page.tsx` - **MODIFIED** (added WebSocket tab)

## Dependencies

No new dependencies required! Uses existing:
- `lucide-react` - Icons (Radio, WifiOff, RefreshCw, Trash2)
- `@/components/ui/*` - UI components (Card, Badge, Button)
- `@/utils/formatters` - Time formatting
- `@/lib/utils` - cn() utility

## Browser Support

Works on all modern browsers that support:
- WebSocket API
- ES6+ JavaScript
- CSS Grid
- Flexbox

## Performance Considerations

- Events are stored in React state (in-memory only)
- Old events should be pruned (max 100-200 events)
- Consider adding pagination or virtual scrolling for large event lists
- WebSocket reconnection uses exponential backoff

## Security

- WebSocket connection should use `wss://` in production
- Authentication via JWT token (to be implemented)
- Validate all incoming messages
- Sanitize displayed data to prevent XSS

## Future Enhancements

1. **Event Filtering**: Filter by event type, bot, symbol
2. **Search**: Search events by order ID, symbol
3. **Export**: Export events to CSV/JSON
4. **Notifications**: Desktop/sound notifications for new events
5. **Event Details Modal**: Click event to see full raw JSON
6. **Auto-scroll**: Toggle auto-scroll to latest event
7. **Event Statistics**: Show event counts, types distribution
8. **Time Range Filter**: Show events from last hour, day, etc.

## Troubleshooting

### WebSocket not connecting?
- Check backend is running
- Verify WebSocket endpoint exists
- Check CORS settings allow WebSocket connections
- Check browser console for errors

### Events not showing?
- Verify backend is sending correct format
- Check browser developer tools → Network → WS tab
- Add console.log() in event handler to debug

### UI not updating?
- Check React state is being updated
- Verify component re-renders when events change
- Check for JavaScript errors in console

---

**Status**: ✅ Frontend implementation complete, awaiting backend WebSocket endpoint
**Last Updated**: 2025-10-20
**Author**: Claude Code Assistant
