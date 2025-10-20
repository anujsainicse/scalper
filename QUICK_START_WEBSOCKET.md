# Quick Start - WebSocket Live Data

## 🚀 Get Started in 3 Minutes!

### Prerequisites
- Python 3.9+
- Node.js 18+
- CoinDCX API credentials in `.env`

---

## Step 1: Install Dependencies (1 min)

```bash
# Backend
cd backend
pip3 install fastapi uvicorn websockets python-socketio[asyncio_client] aiohttp asyncpg pydantic-settings python-telegram-bot

# Frontend (already installed)
cd ..
# No new dependencies needed!
```

---

## Step 2: Start Backend (30 sec)

```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

## Step 3: Start Frontend (30 sec)

```bash
# New terminal
npm run dev
```

**Expected output**:
```
  ▲ Next.js 15.5.6
  - Local:        http://localhost:3000
```

---

## Step 4: Test WebSocket (1 min)

### Open Browser
```
http://localhost:3000
```

### Click WebSocket Tab
- Click the green "WebSocket" button at the bottom
- You should see: **🟢 Live**

### Place Test Order
```bash
# New terminal
cd backend
python3 testcoindcxf_auto.py
```

### Watch the Magic! ✨
Events will appear in the WebSocket tab in real-time:
- 📦 Order created (status: initial)
- 📦 Order placed (status: open)
- 📊 Position updated
- 💰 Balance updated
- 📦 Order cancelled

---

## Troubleshooting

### Backend won't start?
```bash
# Check port 8000 is free
lsof -i :8000

# If occupied, kill it
kill -9 <PID>
```

### WebSocket shows "Disconnected"?
```bash
# Check backend status
curl http://localhost:8000/api/v1/ws/status

# Should return:
# {"active_connections":1,"coindcx_connected":true}
```

### No events showing?
```bash
# Check browser console (F12)
# Look for WebSocket connection

# Check backend logs for errors

# Try placing another order
python3 testcoindcxf_auto.py
```

---

## What You Can Do

✅ **Monitor Orders**: See every order update in real-time
✅ **Track Positions**: Watch position changes as orders fill
✅ **Watch Balance**: See balance updates instantly
✅ **Multiple Clients**: Open multiple browser tabs
✅ **Auto-reconnect**: Closes connection? It reconnects!
✅ **Event History**: Last 100 events kept in memory

---

## Next Actions

### Test Different Scenarios
1. Place multiple orders
2. Cancel orders
3. Let orders fill (if price reached)
4. Watch position changes
5. Monitor balance updates

### Customize
1. Change event card colors
2. Add sound notifications
3. Export events to CSV
4. Filter by event type
5. Search events

---

## Architecture Overview

```
Browser (localhost:3000)
    ↓ WebSocket
Backend FastAPI (localhost:8000/api/v1/ws/coindcx)
    ↓ WebSocket
CoinDCX Futures (wss://stream.coindcx.com)
```

---

## Key Features

- ⚡ **Real-time**: Sub-second latency
- 🔄 **Auto-reconnect**: Never miss an event
- 🎨 **Color-coded**: Orders (blue), Positions (purple), Balance (green)
- 📊 **Rich Details**: Every field displayed
- 🔍 **Debug Mode**: See all raw events
- 💾 **Event History**: Last 100 events cached
- 👥 **Multi-client**: Support multiple browsers

---

## Files You Need

### Backend
- `/backend/app/api/v1/endpoints/websocket.py` ✅ Created
- `/backend/app/api/v1/router.py` ✅ Updated

### Frontend
- `/components/WebSocketMonitor.tsx` ✅ Updated
- `/app/page.tsx` ✅ Already has WebSocket tab

---

## Support

**Documentation**:
- Full guide: `/WEBSOCKET_BRIDGE_COMPLETE.md`
- Backend guide: `/backend/README_WEBSOCKET.md`
- Frontend guide: `/WEBSOCKET_UI.md`

**Test Scripts**:
- `testcoindcxf_ws.py` - Backend WebSocket monitor
- `testcoindcxf_auto.py` - Auto order placement
- `testcoindcxf.py` - Manual order placement

---

**Enjoy your live data! 🎉**
