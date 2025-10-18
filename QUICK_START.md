# Scalper Bot - Quick Start Guide

Get your Scalper Bot up and running in 10 minutes!

## Prerequisites Check

Before starting, verify you have:

```bash
# Check Node.js (need 18.x+)
node --version  # Should show v18.x.x or higher

# Check Python (need 3.9+)
python3 --version  # Should show 3.9.x or higher

# Check PostgreSQL (need 15.x+)
psql --version  # Should show 15.x or higher

# Check if ports are available
lsof -i :3000  # Should return nothing (port free)
lsof -i :8000  # Should return nothing (port free)
```

## 5-Minute Setup

### Step 1: Get the Code (30 seconds)

```bash
git clone <repository-url>
cd scalper
```

### Step 2: Frontend Setup (2 minutes)

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

✅ Frontend now running at: **http://localhost:3000**

### Step 3: Backend Setup (2.5 minutes)

Open a new terminal:

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Database Setup (30 seconds)

```bash
# Create database
createdb scalper_bot

# Configure environment
cp .env.example .env

# Update DATABASE_URL in .env (use your username)
# DATABASE_URL=postgresql+asyncpg://YOUR_USERNAME@localhost:5432/scalper_bot
```

### Step 5: Start Backend (30 seconds)

```bash
# Make sure you're in backend/ with venv activated
uvicorn app.main:app --reload
```

✅ Backend now running at: **http://localhost:8000**

## Verify Installation

### Test 1: Frontend

Open browser to http://localhost:3000

You should see:
- Bot Configuration form on the left
- Active Bots section in the middle (empty)
- Activity Log on the right (empty)

### Test 2: Backend API

```bash
# Test root endpoint
curl http://localhost:8000

# Expected response:
# {"message":"Scalper Bot API","version":"1.0.0","docs":"/docs","status":"running"}

# Test bots endpoint
curl http://localhost:8000/api/v1/bots/

# Expected response:
# []
```

### Test 3: API Documentation

Open browser to: http://localhost:8000/docs

You should see interactive Swagger UI documentation.

## Create Your First Bot

1. Go to http://localhost:3000

2. Fill in the form:
   - **Ticker**: Select "BTC/USDT"
   - **Exchange**: Select "Binance"
   - **First Order**: Select "BUY"
   - **Quantity**: Select "1"
   - **Buy Price**: Enter "45000"
   - **Sell Price**: Enter "46000"
   - **Trailing %**: Select "0.5%"
   - **Infinite Loop**: Check the box

3. Click "Start Bot"

4. You should see:
   - Green success toast notification
   - Bot appears in "Active Bots" section with status "ACTIVE"
   - Activity log shows "Bot started for BTC/USDT on Binance"

## Quick Commands Reference

### Frontend Commands

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm start            # Run production build
npm run lint         # Run ESLint
```

### Backend Commands

```bash
# Always activate venv first!
source venv/bin/activate

# Start server
uvicorn app.main:app --reload

# With custom host/port
uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run tests
pytest

# Format code
black app/

# Type check
mypy app/
```

### Database Commands

```bash
# Create database
createdb scalper_bot

# Delete database
dropdb scalper_bot

# Connect to database
psql scalper_bot

# Backup database
pg_dump scalper_bot > backup.sql

# Restore database
psql scalper_bot < backup.sql

# List databases
psql -l
```

## Common First-Time Issues

### Issue 1: Port 3000 already in use

```bash
# Find what's using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use different port
PORT=3001 npm run dev
```

### Issue 2: PostgreSQL not running

```bash
# Check status
pg_isready

# Start PostgreSQL (macOS with Homebrew)
brew services start postgresql@15

# Start PostgreSQL (Linux)
sudo systemctl start postgresql
```

### Issue 3: Database connection failed

```bash
# Check if database exists
psql -l | grep scalper_bot

# If not, create it
createdb scalper_bot

# Check .env file has correct username
# DATABASE_URL=postgresql+asyncpg://YOUR_USERNAME@localhost:5432/scalper_bot
```

### Issue 4: Python module not found

```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

### Issue 5: CORS errors in browser console

Edit `backend/.env`:
```env
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

Restart backend server.

## Next Steps

### Customize the Bot

1. **Add More Exchanges**: Edit `config/bot-config.ts`
2. **Change Quantities**: Update `QUANTITIES` array
3. **Modify Theme**: Edit `app/globals.css`

### Explore the API

1. Visit http://localhost:8000/docs
2. Try the "Try it out" feature
3. Create, update, and delete bots via API

### Read Full Documentation

- **Full Docs**: See `DOCS.md`
- **API Reference**: Check `/docs` endpoint
- **Backend README**: See `backend/README.md`
- **Frontend README**: See `README.md`

## Development Workflow

### Daily Development

```bash
# Terminal 1 - Frontend
npm run dev

# Terminal 2 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Making Changes

1. **Frontend changes**: Files auto-reload with Fast Refresh
2. **Backend changes**: Server auto-reloads with `--reload` flag
3. **Database changes**: Create migration with Alembic
4. **Config changes**: Restart respective server

### Testing Changes

```bash
# Frontend
# - Just save files and check browser
# - No manual reload needed

# Backend
# - Server reloads automatically
# - Check terminal for errors
# - Test endpoints with curl or Postman
```

## Production Deployment

### Quick Deploy to Vercel (Frontend)

```bash
npm install -g vercel
vercel login
vercel --prod
```

### Quick Deploy to Railway (Backend)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

## Getting Help

### Where to Look

1. **Error in Terminal**: Read the error message carefully
2. **Error in Browser Console**: Check Network tab for API errors
3. **Database Issues**: Check PostgreSQL logs
4. **Frontend Issues**: Check Next.js error overlay

### Getting Support

- **GitHub Issues**: https://github.com/yourusername/scalper/issues
- **Email**: support@example.com
- **Documentation**: `DOCS.md` file

## Tips & Tricks

### Speed Up Development

1. **Use Auto-save**: Enable in your editor
2. **Keep Terminals Open**: Don't restart servers unnecessarily
3. **Use Browser DevTools**: React DevTools + Network tab
4. **Test with curl**: Faster than browser for API testing

### VS Code Extensions (Recommended)

- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Python
- PostgreSQL
- Thunder Client (API testing)
- GitLens

### Chrome Extensions (Recommended)

- React Developer Tools
- Redux DevTools (for future)
- JSON Formatter

## Keyboard Shortcuts

### VS Code
- `Cmd/Ctrl + P`: Quick file open
- `Cmd/Ctrl + Shift + P`: Command palette
- `Cmd/Ctrl + B`: Toggle sidebar
- `Cmd/Ctrl + J`: Toggle terminal

### Chrome DevTools
- `Cmd/Ctrl + Shift + C`: Inspect element
- `Cmd/Ctrl + Shift + J`: Console
- `Cmd/Ctrl + Shift + I`: DevTools

## Checklist

Use this checklist to verify your setup:

- [ ] Node.js 18+ installed
- [ ] Python 3.9+ installed
- [ ] PostgreSQL 15+ installed and running
- [ ] Repository cloned
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Frontend running on port 3000
- [ ] Backend virtual environment created
- [ ] Backend dependencies installed
- [ ] PostgreSQL database created
- [ ] Backend `.env` file configured
- [ ] Backend running on port 8000
- [ ] Can access frontend at http://localhost:3000
- [ ] Can access API at http://localhost:8000
- [ ] Can access API docs at http://localhost:8000/docs
- [ ] Created first test bot successfully
- [ ] Bot appears in Active Bots section
- [ ] Activity log shows bot creation

## What's Next?

Now that you're set up, explore:

1. **Create Multiple Bots**: Try different trading pairs
2. **Edit Bots**: Click edit button, modify, update
3. **View Logs**: Filter by log level, export to CSV
4. **Stop/Start Bots**: Test the bot controls
5. **Emergency Stop**: Try the "Stop All Bots" button
6. **Toggle Theme**: Click the theme toggle button
7. **Connect Telegram**: Test the Telegram connection

## Advanced Topics

Ready for more? Check out:

- **WebSocket Integration**: Real-time price updates
- **Exchange API Integration**: Connect to real exchanges
- **Backtesting**: Test strategies on historical data
- **Risk Management**: Add stop-loss logic
- **Authentication**: Add user accounts
- **Deployment**: Deploy to production

---

**Estimated Setup Time**: 10 minutes
**Difficulty**: Beginner-friendly
**Support**: See `DOCS.md` for detailed documentation

Happy Trading! 🚀
