# Scalper Bot - Project Documentation

## Project Overview

Scalper Bot is a cryptocurrency trading bot management system with a modern web interface. It allows users to configure, manage, and monitor multiple trading bots for automated scalping strategies on various cryptocurrency exchanges.

## Technology Stack

### Frontend
- **Framework**: Next.js 15.5.6 (React 19)
- **Language**: TypeScript
- **State Management**: Zustand
- **UI Components**: shadcn/ui with Tailwind CSS
- **Notifications**: React Hot Toast
- **HTTP Client**: Native Fetch API

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15 with asyncpg driver
- **ORM**: SQLAlchemy 2.0 (Async)
- **Cache**: Redis 7
- **Notifications**: Telegram Bot API
- **Server**: Uvicorn (ASGI)

## Project Structure

```
scalper/
├── app/                          # Next.js app directory
├── components/                   # React components
│   ├── BotConfiguration.tsx     # Bot creation/edit form
│   ├── ActiveBots.tsx           # Bot list and management
│   └── ui/                      # shadcn/ui components
├── store/
│   └── botStore.ts              # Zustand state management
├── lib/
│   └── api.ts                   # API client
├── backend/
│   ├── app/
│   │   ├── api/v1/              # API endpoints
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── core/                # Config, Redis, DB
│   │   └── db/                  # Database session
│   └── alembic/                 # Database migrations (if configured)
├── config/
│   └── bot-config.ts            # Frontend configuration
└── types/
    └── bot.ts                   # TypeScript type definitions
```

## Key Features

### 1. Bot Management
- Create multiple trading bots with custom configurations
- Edit existing bot parameters
- Start/Stop individual bots
- Delete bots
- Emergency stop all bots

### 2. Bot Configuration
- **Exchange Selection**: CoinDCX F, Binance
- **Ticker Selection**: Popular trading pairs (BTC/USDT, ETH/USDT, etc.)
- **Order Type**: BUY or SELL first
- **Pricing**:
  - Buy Price (automatically set 2% below LTP)
  - Sell Price (automatically set 2% above LTP)
  - Percentage-based price adjustment buttons (±0.1%, ±0.5%, ±1%)
- **Quantity**: Integer increment/decrement buttons
- **Trailing Stop**: Optional trailing percentage (0.1% - 3.0%)
- **Infinite Loop**: Toggle for continuous trading

### 3. Real-Time Price Data
- Fetches Last Traded Price (LTP) from Redis
- Displays live market data for selected ticker
- Auto-updates buy/sell prices based on current market price
- Dynamic decimal precision matching LTP format

### 4. Activity Logging
- Comprehensive activity tracking
- Log levels: INFO, SUCCESS, WARNING, ERROR, TELEGRAM
- Filterable by bot and log level
- Reverse chronological order (newest first)

### 5. Telegram Integration
- Real-time notifications for:
  - Bot creation
  - Bot deletion
  - Bot start/stop
  - Emergency stop events
- Connection management via chat ID

## Database Schema

### Bots Table
```sql
CREATE TABLE bots (
    id UUID PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    exchange ENUM('CoinDCX F', 'Binance'),
    first_order ENUM('BUY', 'SELL'),
    quantity FLOAT NOT NULL,
    buy_price FLOAT NOT NULL,
    sell_price FLOAT NOT NULL,
    trailing_percent FLOAT,
    infinite_loop BOOLEAN DEFAULT FALSE,
    status ENUM('ACTIVE', 'STOPPED', 'ERROR') DEFAULT 'STOPPED',
    pnl FLOAT DEFAULT 0.0,
    total_trades INTEGER DEFAULT 0,
    last_fill_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    config JSON
);
```

### Activity Logs Table
```sql
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY,
    bot_id UUID REFERENCES bots(id),
    level VARCHAR(20) NOT NULL,
    message VARCHAR(500) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    extra_data JSON
);
```

### Trades Table
```sql
CREATE TABLE trades (
    id UUID PRIMARY KEY,
    bot_id UUID NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side ENUM('BUY', 'SELL'),
    quantity FLOAT NOT NULL,
    price FLOAT NOT NULL,
    pnl FLOAT,
    commission FLOAT DEFAULT 0.0,
    exchange_order_id VARCHAR(100),
    exchange ENUM('CoinDCX F', 'Binance'),
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    extra_data JSON
);
```

### Telegram Connections Table
```sql
CREATE TABLE telegram_connections (
    id UUID PRIMARY KEY,
    chat_id VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    connection_code VARCHAR(6),
    code_expires_at TIMESTAMP WITH TIME ZONE,
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_notification_at TIMESTAMP WITH TIME ZONE,
    extra_data JSON
);
```

## API Endpoints

### Bot Endpoints
- `GET /api/v1/bots` - List all bots
- `POST /api/v1/bots` - Create new bot
- `GET /api/v1/bots/{bot_id}` - Get bot details
- `PUT /api/v1/bots/{bot_id}` - Update bot
- `DELETE /api/v1/bots/{bot_id}` - Delete bot
- `POST /api/v1/bots/{bot_id}/start` - Start bot
- `POST /api/v1/bots/{bot_id}/stop` - Stop bot
- `POST /api/v1/bots/{bot_id}/toggle` - Toggle bot status
- `POST /api/v1/bots/stop-all` - Emergency stop all bots
- `GET /api/v1/bots/statistics/summary` - Get bot statistics

### Activity Log Endpoints
- `GET /api/v1/logs` - List activity logs (with filters)
- `POST /api/v1/logs` - Create activity log
- `DELETE /api/v1/logs` - Clear all logs
- `GET /api/v1/logs/count` - Get log counts by level

### Price Data Endpoints
- `GET /api/v1/price/ltp?exchange={exchange}&ticker={ticker}` - Get LTP from Redis

### Telegram Endpoints
- `POST /api/v1/telegram/webhook` - Telegram webhook handler
- Additional endpoints for connection management

## Redis Integration

### Redis Keys Structure
- **Format**: `{redis_prefix}:{base_symbol}`
- **Example**: `coindcx_futures:ETH`

### Exchange Mappings
```typescript
{
  'CoinDCX F': 'coindcx_futures',
  'Binance': 'binance_spot',
  'Delta': 'delta_futures',
  'Bybit': 'bybit_spot'
}
```

### Price Data Fields
- `ltp`: Last traded price
- `current_funding_rate`: Current funding rate (for futures)
- `timestamp`: Data timestamp
- Additional exchange-specific fields

## Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/scalper_bot

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Telegram (Optional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/telegram/webhook

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Frontend Setup
```bash
cd scalper
npm install
npm run dev
```

### Backend Setup
```bash
cd scalper/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Setup
```bash
# Create PostgreSQL database
createdb scalper_bot

# Run migrations (if using Alembic)
alembic upgrade head
```

## Recent Updates

### UI Enhancements
- Implemented percentage-based price adjustment buttons (±0.1%, ±0.5%, ±1%)
- Added dynamic decimal precision matching LTP format
- Reorganized form field layout for better UX
- Moved LTP display inline with "First Order" section
- Default buy/sell prices auto-calculate at ±2% from LTP

### Bug Fixes
- Fixed delete bot error (204 No Content response handling)
- Fixed buy/sell price reset after bot creation
- Improved activity log ordering (newest first)

### Performance Optimizations
- Async database operations with SQLAlchemy
- Redis caching for price data
- Optimized API client error handling

## Known Issues & Limitations
- Bot deletion takes ~2 seconds due to Telegram notification and log refresh
- No real trading execution implemented (framework only)
- Limited to configured exchanges (CoinDCX F, Binance)

## Future Enhancements
- Real exchange integration for actual trading
- Advanced order types (limit, stop-loss, take-profit)
- Backtesting engine
- Performance analytics dashboard
- Multi-user support with authentication
- WebSocket support for real-time updates

## Development Notes

### Code Style
- Frontend: TypeScript with strict mode
- Backend: Python with type hints
- Components: Functional components with hooks
- API: RESTful design principles

### Testing
- Unit tests: Jest (frontend), pytest (backend)
- Integration tests: End-to-end API testing
- Manual testing: Development environment

## License
[Specify your license here]

## Author
Anuj Saini

## Repository
[Add repository URL here]

---

Last Updated: January 2025
