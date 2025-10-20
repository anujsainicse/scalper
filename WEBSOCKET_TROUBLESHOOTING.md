# WebSocket Troubleshooting Guide

## Common Issues and Solutions

### Issue: "WebSocket error: {}" in Browser Console

**Symptoms**:
- Browser console shows `❌ WebSocket error: {}`
- WebSocket tab shows "🔴 Disconnected"
- No events appearing in the UI

**Causes & Solutions**:

#### 1. Backend Not Running
```bash
# Check if backend is running
curl http://localhost:8000/api/v1/ws/status

# If fails, start backend
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 2. Backend Started with --reload (Subprocess Issue)
The `--reload` flag can cause subprocess issues with missing dependencies.

**Solution**: Start without --reload
```bash
# Instead of this:
python3 -m uvicorn app.main:app --reload

# Use this:
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 3. Dependencies Not Installed
```bash
# Install required packages
pip3 install fastapi uvicorn websockets python-socketio[asyncio_client] aiohttp asyncpg pydantic-settings pytz

# Key package for timezone fix
pip3 install pytz
```

#### 4. Wrong WebSocket URL
Check the URL in `/components/WebSocketMonitor.tsx`:
```typescript
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/ws/coindcx';
```

Should be: `ws://localhost:8000/api/v1/ws/coindcx` (NOT wss:// in development)

#### 5. CORS Issues
The backend should have CORS configured for WebSocket. Check `/backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Verification Steps

### 1. Check Backend Status
```bash
curl http://localhost:8000/api/v1/ws/status
```

**Expected Response**:
```json
{
  "active_connections": 1,
  "coindcx_connected": true
}
```

### 2. Check WebSocket Endpoint Exists
```bash
curl http://localhost:8000/docs
```

Look for `/api/v1/ws/coindcx` in the Swagger UI.

### 3. Test WebSocket Connection Manually
Open browser console (F12) and run:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/coindcx');
ws.onopen = () => console.log('✅ Connected');
ws.onmessage = (e) => console.log('📡', JSON.parse(e.data));
ws.onerror = (e) => console.log('❌ Error', e);
```

### 4. Check Backend Logs
Look for these messages:
```
INFO: New WebSocket connection. Total: 1
INFO: Connecting to CoinDCX WebSocket...
INFO: ✅ Connected to CoinDCX WebSocket
```

### 5. Place Test Order
```bash
cd backend
python3 testcoindcxf_auto.py
```

Should see in backend logs:
```
INFO: 📦 Order Update: order-id - open
INFO: 📊 Position Update: B-ETH_USDT
INFO: 💰 Balance Update: INR
```

---

## Quick Fix Checklist

- [ ] Backend is running: `curl localhost:8000`
- [ ] WebSocket endpoint exists: `curl localhost:8000/api/v1/ws/status`
- [ ] Frontend is running: Browser at `localhost:3000`
- [ ] WebSocket URL is correct in component
- [ ] Dependencies installed: `pip3 install -r requirements.txt`
- [ ] CoinDCX credentials in `.env`
- [ ] No firewall blocking WebSocket
- [ ] Browser supports WebSocket (all modern browsers do)

---

## Dependency Issues

### Telegram Bot Error (Non-Critical)
```
ERROR: Failed to initialize Telegram bot: Only timezones from the pytz library are supported
```

**Solution**:
```bash
pip3 install pytz
```

This error won't prevent WebSocket from working, but it's good to fix.

### AsyncPG Missing
```
ModuleNotFoundError: No module named 'asyncpg'
```

**Solution**:
```bash
pip3 install asyncpg
```

### Python-SocketIO Missing
```
ModuleNotFoundError: No module named 'socketio'
```

**Solution**:
```bash
pip3 install python-socketio[asyncio_client] aiohttp
```

---

## Browser Console Debugging

### Enable Verbose Logging
In `WebSocketMonitor.tsx`, all events are already logged:
```typescript
console.log('Connecting to WebSocket:', WS_URL);
console.log('✅ WebSocket connected');
console.log('📡 Event received:', data.type, data.data);
```

### Check Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Filter by "WS" (WebSocket)
4. Should see connection to `ws://localhost:8000/api/v1/ws/coindcx`
5. Click it to see frames (messages)

---

## Connection States

### 🟢 Live (Good)
- WebSocket connected
- Backend connected to CoinDCX
- Events flowing

### 🟡 Reconnecting (Transient)
- Connection lost
- Auto-reconnect in progress
- Will retry every 5 seconds

### 🔴 Disconnected (Problem)
- No connection to backend
- Check backend is running
- Check URL is correct
- Check for errors in console

---

## Testing Without Orders

You can test WebSocket without placing orders:

### 1. Check Connection Status Message
When you connect, you should see:
```json
{
  "type": "system",
  "data": {
    "message": "Connected to CoinDCX WebSocket bridge",
    "coindcx_connected": true
  }
}
```

### 2. Monitor Any CoinDCX Activity
If there's any activity on your CoinDCX account (orders from other sources, position changes, balance updates), they'll appear in the WebSocket monitor.

---

## Performance Issues

### Too Many Events Slowing Down UI
Events are capped at 100. If still slow:

**Option 1**: Reduce cap in `WebSocketMonitor.tsx`:
```typescript
.slice(0, 50)  // Instead of 100
```

**Option 2**: Add virtualization:
```bash
npm install react-window
```

### High CPU Usage
- Check for infinite reconnect loops
- Check browser console for errors
- Restart both frontend and backend

---

## Production Deployment

### Use WSS (Secure WebSocket)
```typescript
const WS_URL = 'wss://your-domain.com/api/v1/ws/coindcx';
```

### Add Authentication
Backend should check token:
```python
@router.websocket("/coindcx")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Verify token
    if not verify_jwt_token(token):
        await websocket.close(code=1008)
        return
    # ... rest of code
```

Frontend should send token:
```typescript
const ws = new WebSocket(
  `${WS_URL}?token=${getAuthToken()}`
);
```

---

## Still Not Working?

### 1. Restart Everything
```bash
# Kill all processes
pkill -f uvicorn
pkill -f "next dev"

# Start backend
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start frontend (new terminal)
npm run dev
```

### 2. Check Firewall
```bash
# macOS
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Linux
sudo ufw status
```

### 3. Check Port Availability
```bash
# Check if port 8000 is in use
lsof -i :8000

# Check if port 3000 is in use
lsof -i :3000
```

### 4. Try Different Port
Backend:
```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Frontend (update `WS_URL`):
```typescript
const WS_URL = 'ws://localhost:8001/api/v1/ws/coindcx';
```

---

## Success Indicators

✅ Backend logs show:
```
INFO: New WebSocket connection. Total: 1
INFO: ✅ Connected to CoinDCX WebSocket
```

✅ Browser console shows:
```
Connecting to WebSocket: ws://localhost:8000/api/v1/ws/coindcx
✅ WebSocket connected
System message: Connected to CoinDCX WebSocket bridge
```

✅ UI shows:
- 🟢 Live status badge
- No errors in console
- Events appear when orders placed

---

## Get Help

If none of these solutions work:

1. Check all documentation files:
   - `/WEBSOCKET_BRIDGE_COMPLETE.md`
   - `/QUICK_START_WEBSOCKET.md`
   - `/backend/README_WEBSOCKET.md`

2. Check backend logs for errors

3. Check browser console for errors

4. Verify CoinDCX API credentials are valid

5. Test CoinDCX connection directly:
   ```bash
   python3 testcoindcxf_ws.py monitor
   ```

---

**Last Updated**: 2025-10-20
