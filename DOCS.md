# Scalper Bot - Complete Documentation

Comprehensive documentation for the Scalper Bot cryptocurrency trading platform.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Installation Guide](#installation-guide)
4. [Configuration](#configuration)
5. [API Reference](#api-reference)
6. [Database Schema](#database-schema)
7. [State Management](#state-management)
8. [Component Documentation](#component-documentation)
9. [Deployment Guide](#deployment-guide)
10. [Security Best Practices](#security-best-practices)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

---

## Project Overview

### What is Scalper Bot?

Scalper Bot is a full-stack cryptocurrency trading platform that enables users to:
- Create and manage automated trading bots
- Monitor bot performance in real-time
- Track profit/loss across multiple trading pairs
- Receive notifications via Telegram
- Analyze trading activity with comprehensive logs

### Technology Stack

**Frontend**
```
Next.js 15.5.6 + React 19.1.0 + TypeScript
├── UI Framework: shadcn/ui (Radix UI primitives)
├── Styling: Tailwind CSS 3.4.1
├── State: Zustand 5.0.2
├── Notifications: react-hot-toast 2.4.1
└── Icons: Lucide React 0.468.0
```

**Backend**
```
FastAPI 0.109.0 + Python 3.9+
├── ORM: SQLAlchemy 2.0.25 (async)
├── Database: PostgreSQL 15+
├── Validation: Pydantic 2.5.3
├── Server: Uvicorn (ASGI)
└── Migrations: Alembic 1.13.1
```

---

## Architecture

### System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Client Browser                         │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Next.js Application (Port 3000)          │    │
│  │  ┌────────────────┐        ┌──────────────┐     │    │
│  │  │   Components   │◄──────►│ Zustand Store│     │    │
│  │  └────────────────┘        └──────────────┘     │    │
│  └─────────────────────┬───────────────────────────┘    │
└────────────────────────┼──────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌──────────────────────────────────────────────────────────┐
│         FastAPI Backend (Port 8000)                      │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   Routers  │─►│  Endpoints   │─►│   Services     │  │
│  └────────────┘  └──────────────┘  └────────────────┘  │
│                          │                               │
│                          ▼                               │
│  ┌────────────────────────────────────────────────────┐ │
│  │         SQLAlchemy ORM (Async)                     │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│              PostgreSQL Database                         │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   bots   │  │activity_logs │  │     trades       │  │
│  └──────────┘  └──────────────┘  └──────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Request Flow

1. **User Action** → Component event handler
2. **State Update** → Zustand store action
3. **API Call** → HTTP request to FastAPI
4. **Backend Processing** → Endpoint → Service → Database
5. **Response** → JSON data back to frontend
6. **UI Update** → React re-render + Toast notification
7. **Logging** → Activity log entry created

### Data Flow

```
Component → Zustand Store → API Request → FastAPI Endpoint
    ↓                                           ↓
Toast Notification                     Database Operation
    ↓                                           ↓
Activity Log                            Response Data
    ↓                                           ↓
UI Update ←─────────────────────────────  JSON Response
```

---

## Installation Guide

### Prerequisites

Before installation, ensure you have:

- **Node.js**: 18.x or higher ([Download](https://nodejs.org/))
- **Python**: 3.9 or higher ([Download](https://python.org/))
- **PostgreSQL**: 15.x or higher ([Download](https://postgresql.org/))
- **Git**: Latest version ([Download](https://git-scm.com/))

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd scalper
```

### Step 2: Frontend Setup

```bash
# Install Node.js dependencies
npm install

# Create environment file
touch .env.local

# Add the following to .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:3000**

### Step 3: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
# venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Database Setup

```bash
# Install PostgreSQL (macOS with Homebrew)
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Create database
createdb scalper_bot

# Or using psql
psql -U postgres
CREATE DATABASE scalper_bot;
\q
```

### Step 5: Configure Backend

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env
```

Update these critical variables:
```env
DATABASE_URL=postgresql+asyncpg://your_username@localhost:5432/scalper_bot
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
DEBUG=True
```

### Step 6: Start Backend Server

```bash
# Make sure you're in backend directory with venv activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Verification

Test the installation:

```bash
# Test frontend
curl http://localhost:3000

# Test backend
curl http://localhost:8000

# Test API
curl http://localhost:8000/api/v1/bots/
```

---

## Configuration

### Frontend Configuration

**File: `.env.local`**
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Analytics
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Optional: Feature Flags
NEXT_PUBLIC_ENABLE_TELEGRAM=true
NEXT_PUBLIC_ENABLE_EXPORT=true
```

**File: `config/bot-config.ts`**
```typescript
// Exchanges configuration
export const EXCHANGES: ConfigItem[] = [
  { value: 'CoinDCX F', label: 'CoinDCX F' },
  { value: 'Binance', label: 'Binance' },
  // Add more exchanges here
];

// Quantities configuration
export const QUANTITIES: ConfigItem[] = [
  { value: 1, label: '1' },
  { value: 2, label: '2' },
  { value: 3, label: '3' },
  { value: 5, label: '5' },
  { value: 10, label: '10' },
  { value: 0, label: 'Custom' },
];

// Trailing stop percentages
export const TRAILING_PERCENTAGES: ConfigItem[] = [
  { value: 'none', label: 'None' },
  { value: '0.1', label: '0.1%' },
  { value: '0.5', label: '0.5%' },
  { value: '1', label: '1%' },
];

// Popular trading pairs
export const POPULAR_TICKERS: string[] = [
  'BTC/USDT',
  'ETH/USDT',
  'SOL/USDT',
  'BNB/USDT',
];
```

### Backend Configuration

**File: `backend/.env`**

```env
# ============================================
# API Settings
# ============================================
API_V1_STR=/api/v1
PROJECT_NAME=Scalper Bot API
VERSION=1.0.0
DESCRIPTION=API for cryptocurrency scalping bot management

# ============================================
# Server Settings
# ============================================
HOST=0.0.0.0
PORT=8000
DEBUG=True
WORKERS=4

# ============================================
# Database Settings
# ============================================
# Format: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
DATABASE_URL=postgresql+asyncpg://anujsainicse@localhost:5432/scalper_bot
DB_ECHO_LOG=False
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# ============================================
# Redis Settings (Optional)
# ============================================
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=
REDIS_DB=0

# ============================================
# Security
# ============================================
# Generate with: openssl rand -hex 32
SECRET_KEY=your-super-secret-key-change-this-in-production-minimum-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================
# CORS Origins
# ============================================
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# ============================================
# Exchange API Keys (Optional, for live trading)
# ============================================
BYBIT_API_KEY=your-api-key-here
BYBIT_SECRET_KEY=your-secret-key-here
BYBIT_TESTNET=True

BINANCE_API_KEY=your-api-key-here
BINANCE_SECRET_KEY=your-secret-key-here
BINANCE_TESTNET=True

# ============================================
# WebSocket Settings
# ============================================
WS_HEARTBEAT_INTERVAL=30
WS_MESSAGE_QUEUE_SIZE=100

# ============================================
# Bot Settings
# ============================================
MAX_BOTS_PER_USER=10
DEFAULT_BOT_STATUS=STOPPED
MIN_TRADE_AMOUNT=0.001
MAX_TRADE_AMOUNT=1000

# ============================================
# Telegram Settings (Optional)
# ============================================
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# ============================================
# Logging
# ============================================
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_PATH=logs/app.log

# ============================================
# Rate Limiting
# ============================================
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

**File: `backend/app/core/config.py`**

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Scalper Bot API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for cryptocurrency scalping bot management"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Database
    DATABASE_URL: str
    DB_ECHO_LOG: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001"
    ]

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Bot Settings
    MAX_BOTS_PER_USER: int = 10
    DEFAULT_BOT_STATUS: str = "STOPPED"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## API Reference

### Base URL

```
Development: http://localhost:8000
Production: https://api.scalperbot.com
```

### Authentication

Currently no authentication required (development mode).

Future: JWT Bearer token authentication.

```http
Authorization: Bearer <token>
```

### Common Headers

```http
Content-Type: application/json
Accept: application/json
```

### Bot Endpoints

#### 1. List All Bots

```http
GET /api/v1/bots/
```

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum records to return (default: 100)
- `status` (string, optional): Filter by status (ACTIVE, STOPPED)

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "ticker": "BTC/USDT",
    "exchange": "Binance",
    "first_order": "BUY",
    "quantity": 0.01,
    "buy_price": 45000.50,
    "sell_price": 46000.00,
    "trailing_percent": 1.5,
    "infinite_loop": true,
    "status": "ACTIVE",
    "pnl": 125.50,
    "total_trades": 10,
    "last_fill_time": "2024-01-01T10:30:00Z",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:30:00Z"
  }
]
```

#### 2. Create Bot

```http
POST /api/v1/bots/
```

**Request Body:**
```json
{
  "ticker": "BTC/USDT",
  "exchange": "Binance",
  "first_order": "BUY",
  "quantity": 0.01,
  "buy_price": 45000.50,
  "sell_price": 46000.00,
  "trailing_percent": 1.5,
  "infinite_loop": true
}
```

**Response:** (201 Created)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "ticker": "BTC/USDT",
  "exchange": "Binance",
  "first_order": "BUY",
  "quantity": 0.01,
  "buy_price": 45000.50,
  "sell_price": 46000.00,
  "trailing_percent": 1.5,
  "infinite_loop": true,
  "status": "ACTIVE",
  "pnl": 0.0,
  "total_trades": 0,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

#### 3. Get Bot by ID

```http
GET /api/v1/bots/{bot_id}
```

**Path Parameters:**
- `bot_id` (UUID, required): Bot identifier

**Response:** (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "ticker": "BTC/USDT",
  "exchange": "Binance",
  "status": "ACTIVE",
  "pnl": 125.50,
  "total_trades": 10
}
```

**Error Response:** (404 Not Found)
```json
{
  "detail": "Bot not found"
}
```

#### 4. Update Bot

```http
PUT /api/v1/bots/{bot_id}
```

**Request Body:** (all fields optional)
```json
{
  "quantity": 0.02,
  "buy_price": 44000.00,
  "sell_price": 45500.00,
  "trailing_percent": 2.0
}
```

**Response:** (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "ticker": "BTC/USDT",
  "quantity": 0.02,
  "buy_price": 44000.00,
  "sell_price": 45500.00,
  "trailing_percent": 2.0,
  "updated_at": "2024-01-01T11:00:00Z"
}
```

#### 5. Delete Bot

```http
DELETE /api/v1/bots/{bot_id}
```

**Response:** (204 No Content)

#### 6. Start Bot

```http
POST /api/v1/bots/{bot_id}/start
```

**Response:** (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ACTIVE",
  "updated_at": "2024-01-01T11:00:00Z"
}
```

#### 7. Stop Bot

```http
POST /api/v1/bots/{bot_id}/stop
```

**Response:** (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "STOPPED",
  "updated_at": "2024-01-01T11:00:00Z"
}
```

#### 8. Toggle Bot Status

```http
POST /api/v1/bots/{bot_id}/toggle
```

**Response:** (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ACTIVE",
  "updated_at": "2024-01-01T11:00:00Z"
}
```

#### 9. Stop All Bots

```http
POST /api/v1/bots/stop-all
```

**Response:** (200 OK)
```json
{
  "message": "Stopped 5 bots",
  "count": 5
}
```

#### 10. Get Statistics

```http
GET /api/v1/bots/statistics/summary
```

**Response:** (200 OK)
```json
{
  "total_bots": 10,
  "active_bots": 7,
  "stopped_bots": 3,
  "total_pnl": 1250.75,
  "total_trades": 156
}
```

### Activity Log Endpoints

#### 1. List Logs

```http
GET /api/v1/logs/
```

**Query Parameters:**
- `skip` (integer, optional): Records to skip
- `limit` (integer, optional): Max records
- `level` (string, optional): Filter by level

**Response:**
```json
[
  {
    "id": "650e8400-e29b-41d4-a716-446655440001",
    "bot_id": "550e8400-e29b-41d4-a716-446655440000",
    "level": "SUCCESS",
    "message": "Bot started for BTC/USDT on Binance",
    "timestamp": "2024-01-01T10:00:00Z"
  }
]
```

#### 2. Create Log

```http
POST /api/v1/logs/
```

**Request Body:**
```json
{
  "bot_id": "550e8400-e29b-41d4-a716-446655440000",
  "level": "INFO",
  "message": "Custom log message"
}
```

#### 3. Clear All Logs

```http
DELETE /api/v1/logs/
```

**Response:** (200 OK)
```json
{
  "message": "All logs cleared",
  "count": 150
}
```

#### 4. Get Log Counts

```http
GET /api/v1/logs/count
```

**Response:**
```json
{
  "INFO": 50,
  "SUCCESS": 30,
  "WARNING": 15,
  "ERROR": 5,
  "TELEGRAM": 10,
  "total": 110
}
```

### Error Responses

All endpoints may return these errors:

**400 Bad Request**
```json
{
  "detail": "Invalid input data",
  "errors": [
    {
      "field": "buy_price",
      "message": "Must be greater than 0"
    }
  ]
}
```

**404 Not Found**
```json
{
  "detail": "Bot not found"
}
```

**422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "buy_price"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal server error",
  "request_id": "req_123456"
}
```

---

## Database Schema

### Tables Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│      bots       │     │ activity_logs   │     │     trades      │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK, UUID)   │◄────│ bot_id (FK)     │     │ id (PK, UUID)   │
│ ticker          │     │ level           │     │ bot_id (FK)     │
│ exchange        │     │ message         │     │ symbol          │
│ first_order     │     │ timestamp       │     │ side            │
│ quantity        │     │ extra_data      │     │ quantity        │
│ buy_price       │     └─────────────────┘     │ price           │
│ sell_price      │                             │ pnl             │
│ trailing_percent│                             │ commission      │
│ infinite_loop   │                             │ exchange_order_id│
│ status          │                             │ exchange        │
│ pnl             │                             │ executed_at     │
│ total_trades    │                             │ extra_data      │
│ last_fill_time  │                             └─────────────────┘
│ created_at      │
│ updated_at      │
│ config (JSON)   │
└─────────────────┘
```

### Table: `bots`

Stores bot configuration and status.

```sql
CREATE TABLE bots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(20) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    first_order VARCHAR(10) NOT NULL,
    quantity NUMERIC(20, 8) NOT NULL,
    buy_price NUMERIC(20, 8) NOT NULL,
    sell_price NUMERIC(20, 8) NOT NULL,
    trailing_percent NUMERIC(5, 2),
    infinite_loop BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'STOPPED',
    pnl NUMERIC(20, 8) DEFAULT 0.0,
    total_trades INTEGER DEFAULT 0,
    last_fill_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    config JSONB,

    CHECK (quantity > 0),
    CHECK (buy_price > 0),
    CHECK (sell_price > buy_price),
    CHECK (trailing_percent >= 0 AND trailing_percent <= 100)
);

CREATE INDEX idx_bots_status ON bots(status);
CREATE INDEX idx_bots_ticker ON bots(ticker);
CREATE INDEX idx_bots_created_at ON bots(created_at DESC);
```

**Columns:**
- `id`: Unique identifier (UUID)
- `ticker`: Trading pair (e.g., "BTC/USDT")
- `exchange`: Exchange name (Enum: Binance, CoinDCX F)
- `first_order`: Initial order type (Enum: BUY, SELL)
- `quantity`: Amount to trade
- `buy_price`: Target buy price
- `sell_price`: Target sell price
- `trailing_percent`: Trailing stop percentage (nullable)
- `infinite_loop`: Whether to trade continuously
- `status`: Bot status (Enum: ACTIVE, STOPPED, ERROR)
- `pnl`: Profit/Loss
- `total_trades`: Number of trades executed
- `last_fill_time`: Last trade execution time
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `config`: Additional JSON configuration

### Table: `activity_logs`

Stores all system activity and events.

```sql
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id UUID REFERENCES bots(id) ON DELETE SET NULL,
    level VARCHAR(20) NOT NULL,
    message VARCHAR(500) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    extra_data JSONB,

    CHECK (level IN ('INFO', 'SUCCESS', 'WARNING', 'ERROR', 'TELEGRAM'))
);

CREATE INDEX idx_logs_bot_id ON activity_logs(bot_id);
CREATE INDEX idx_logs_level ON activity_logs(level);
CREATE INDEX idx_logs_timestamp ON activity_logs(timestamp DESC);
```

**Columns:**
- `id`: Unique identifier (UUID)
- `bot_id`: Associated bot (nullable, foreign key)
- `level`: Log severity level
- `message`: Log message (max 500 chars)
- `timestamp`: When the log was created
- `extra_data`: Additional JSON metadata

### Table: `trades`

Stores trade execution records.

```sql
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id UUID NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    quantity NUMERIC(20, 8) NOT NULL,
    price NUMERIC(20, 8) NOT NULL,
    pnl NUMERIC(20, 8),
    commission NUMERIC(20, 8) DEFAULT 0.0,
    exchange_order_id VARCHAR(100),
    exchange VARCHAR(50) NOT NULL,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    extra_data JSONB,

    CHECK (quantity > 0),
    CHECK (price > 0),
    CHECK (side IN ('BUY', 'SELL'))
);

CREATE INDEX idx_trades_bot_id ON trades(bot_id);
CREATE INDEX idx_trades_executed_at ON trades(executed_at DESC);
CREATE INDEX idx_trades_symbol ON trades(symbol);
```

**Columns:**
- `id`: Unique identifier (UUID)
- `bot_id`: Bot that executed the trade
- `symbol`: Trading pair
- `side`: BUY or SELL
- `quantity`: Amount traded
- `price`: Execution price
- `pnl`: Profit/Loss for this trade
- `commission`: Trading fees
- `exchange_order_id`: Exchange's order ID
- `exchange`: Exchange name
- `executed_at`: Execution timestamp
- `extra_data`: Additional JSON metadata

### Relationships

```
bots (1) ──────► (N) activity_logs
     └─────────► (N) trades
```

- One bot can have many activity logs
- One bot can have many trades
- Deleting a bot cascades to trades
- Deleting a bot sets bot_id to NULL in logs

---

## State Management

### Zustand Store Architecture

**File: `store/botStore.ts`**

```typescript
interface BotStore {
  // State
  bots: ActiveBot[];
  logs: ActivityLog[];
  editingBot: ActiveBot | null;
  telegramConnected: boolean;

  // Bot Actions
  addBot: (bot: BotFormData) => void;
  removeBot: (id: string) => void;
  updateBot: (id: string, updates: Partial<ActiveBot>) => void;
  updateBotFromForm: (id: string, formData: BotFormData) => void;
  toggleBot: (id: string) => void;
  stopAllBots: () => void;
  setEditingBot: (bot: ActiveBot | null) => void;

  // Log Actions
  addLog: (log: Omit<ActivityLog, 'id' | 'timestamp'>) => void;
  clearLogs: () => void;

  // Telegram
  toggleTelegram: () => void;
}
```

### State Structure

```typescript
{
  bots: [
    {
      id: "uuid-1",
      ticker: "BTC/USDT",
      exchange: "Binance",
      status: "ACTIVE",
      pnl: 125.50,
      totalTrades: 10,
      // ... more fields
    }
  ],
  logs: [
    {
      id: "uuid-2",
      level: "SUCCESS",
      message: "Bot started",
      timestamp: Date,
      botId: "uuid-1"
    }
  ],
  editingBot: null,
  telegramConnected: false
}
```

### Action Examples

**Adding a Bot:**
```typescript
const { addBot, addLog } = useBotStore();

// Create bot
const botData: BotFormData = {
  ticker: "BTC/USDT",
  exchange: "Binance",
  firstOrder: "BUY",
  quantity: 0.01,
  buyPrice: 45000,
  sellPrice: 46000,
  trailingPercent: 1.5,
  infiniteLoop: true
};

// Add to store
addBot(botData);

// This automatically:
// 1. Creates bot with ACTIVE status
// 2. Adds SUCCESS log entry
// 3. Updates PnL to 0
// 4. Sets totalTrades to 0
```

**Updating a Bot:**
```typescript
const { updateBot } = useBotStore();

updateBot("bot-id", {
  quantity: 0.02,
  buyPrice: 44000,
  sellPrice: 45500
});
```

**Toggling Bot Status:**
```typescript
const { toggleBot } = useBotStore();

toggleBot("bot-id");
// Switches ACTIVE ↔ STOPPED
// Adds log entry
// Shows toast notification
```

---

## Component Documentation

### BotConfiguration Component

**Purpose**: Form for creating and editing bot configurations

**Props**: None (uses Zustand store)

**State**:
```typescript
{
  ticker: string,
  exchange: Exchange,
  firstOrder: OrderSide,
  quantity: number,
  customQuantity: number,
  buyPrice: number,
  sellPrice: number,
  trailingPercent: string,
  infiniteLoop: boolean,
  errors: string[]
}
```

**Key Functions**:
- `validateForm()`: Validates all form fields
- `handleSubmit()`: Creates or updates bot
- `handleCancel()`: Exits edit mode
- `resetForm()`: Clears all fields

**Usage**:
```tsx
<BotConfiguration />
```

### ActiveBots Component

**Purpose**: Displays and manages all active bots

**Props**: None (uses Zustand store)

**Features**:
- Responsive grid (1/2/3 columns)
- Individual bot cards
- Start/Stop controls
- Edit/Delete actions
- Emergency stop all
- Delete confirmation

**Usage**:
```tsx
<ActiveBots />
```

### ActivityLog Component

**Purpose**: Displays and filters activity logs

**Props**: None (uses Zustand store)

**State**:
```typescript
{
  activeFilter: LogLevel | 'ALL',
  autoScroll: boolean
}
```

**Features**:
- Tab-based filtering
- Auto-scroll toggle
- CSV export
- Clear logs
- Counter badges

**Usage**:
```tsx
<ActivityLog />
```

### TelegramConnect Component

**Purpose**: Manages Telegram connection status

**Props**: None (uses Zustand store)

**Features**:
- Connection toggle
- Visual status indicator
- Toast notifications
- Responsive button text

**Usage**:
```tsx
<TelegramConnect />
```

### ThemeToggle Component

**Purpose**: Switches between light and dark themes

**Props**: None (uses next-themes)

**Features**:
- Icon-based toggle
- Smooth transitions
- Persisted preference
- System theme detection

**Usage**:
```tsx
<ThemeToggle />
```

---

## Deployment Guide

### Frontend Deployment (Vercel)

1. **Prepare for deployment**
```bash
npm run build
npm start # Test production build locally
```

2. **Deploy to Vercel**
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

3. **Configure environment variables** in Vercel dashboard:
```
NEXT_PUBLIC_API_URL=https://api.your-domain.com
```

### Backend Deployment (Docker + AWS)

1. **Create Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

2. **Build and test Docker image**
```bash
# Build
docker build -t scalper-bot-api .

# Test locally
docker run -p 8000:8000 --env-file .env scalper-bot-api

# Test endpoint
curl http://localhost:8000
```

3. **Deploy to AWS ECS**
```bash
# Login to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag scalper-bot-api:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/scalper-bot-api:latest

# Push to ECR
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/scalper-bot-api:latest

# Create ECS task definition and service (use AWS Console or CLI)
```

### Database Deployment (AWS RDS)

1. **Create RDS PostgreSQL instance**
   - Engine: PostgreSQL 15
   - Instance class: db.t3.micro (dev) or db.t3.medium (prod)
   - Storage: 20GB SSD
   - Enable automated backups
   - Enable Multi-AZ (production)

2. **Update connection string**
```env
DATABASE_URL=postgresql+asyncpg://username:password@database.region.rds.amazonaws.com:5432/scalper_bot
```

3. **Run migrations**
```bash
# Connect to container
docker exec -it container-id /bin/bash

# Run migrations
alembic upgrade head
```

### Environment Variables (Production)

```env
# Security
DEBUG=False
SECRET_KEY=<generated-with-openssl-rand-hex-32>

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@rds-endpoint:5432/scalper_bot
DB_POOL_SIZE=20

# CORS
BACKEND_CORS_ORIGINS=["https://scalperbot.com"]

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=WARNING
```

### SSL/TLS Setup

1. **Get SSL certificate** (Let's Encrypt or AWS Certificate Manager)

2. **Configure nginx reverse proxy**
```nginx
server {
    listen 443 ssl http2;
    server_name api.scalperbot.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Security Best Practices

### 1. API Security

**Input Validation**
- All inputs validated with Pydantic
- SQL injection prevented by SQLAlchemy
- XSS prevented by React

**Rate Limiting** (to implement)
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/bots/")
@limiter.limit("60/minute")
async def get_bots():
    pass
```

**Authentication** (to implement)
```python
from fastapi import Depends, HTTPException
from jose import JWTError, jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(401, "Invalid credentials")
```

### 2. Database Security

**Connection Pooling**
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections
    pool_recycle=3600    # Recycle after 1 hour
)
```

**Prepared Statements** (automatic with SQLAlchemy)
```python
# Safe - parameterized
result = await db.execute(
    select(Bot).where(Bot.ticker == ticker)
)

# Unsafe - never do this
query = f"SELECT * FROM bots WHERE ticker = '{ticker}'"  # ❌ SQL Injection risk
```

### 3. Environment Variables

**Never commit secrets**
```bash
# .gitignore
.env
.env.local
.env.production

# backend/.gitignore
.env
venv/
__pycache__/
*.pyc
```

**Use strong secrets**
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate password
openssl rand -base64 32
```

### 4. CORS Configuration

**Development**
```python
CORS_ORIGINS = ["http://localhost:3000"]
```

**Production**
```python
CORS_ORIGINS = [
    "https://scalperbot.com",
    "https://www.scalperbot.com"
]
```

### 5. HTTPS Only

**Force HTTPS in production**
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if not DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 6. Security Headers

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["scalperbot.com"])
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

## Troubleshooting

### Common Issues

#### 1. Frontend won't start

**Error**: `Module not found` or `Cannot find module`

**Solution**:
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Next.js cache
rm -rf .next
npm run dev
```

#### 2. Backend connection refused

**Error**: `Connection refused` or `Cannot connect to database`

**Solution**:
```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL
brew services start postgresql@15

# Check connection
psql -U your_username -d scalper_bot
```

#### 3. Database migration failed

**Error**: `Target database is not up to date`

**Solution**:
```bash
cd backend
source venv/bin/activate

# Check current revision
alembic current

# Upgrade to latest
alembic upgrade head

# If stuck, stamp current version
alembic stamp head
```

#### 4. Port already in use

**Error**: `EADDRINUSE: address already in use :::3000`

**Solution**:
```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different port
PORT=3001 npm run dev
```

#### 5. CORS errors in browser

**Error**: `Access-Control-Allow-Origin` error

**Solution**:
Check backend CORS configuration in `.env`:
```env
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

And in `config.py`:
```python
BACKEND_CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:3001"
]
```

#### 6. Import errors in Python

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Make sure you're in backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Run from correct directory
uvicorn app.main:app --reload
```

---

## FAQ

### General Questions

**Q: Can I use this for real trading?**
A: Currently, this is a development/demo version. For real trading, you need to:
- Integrate actual exchange APIs
- Implement proper error handling
- Add risk management systems
- Test thoroughly with paper trading first
- Never trade with funds you can't afford to lose

**Q: Which exchanges are supported?**
A: Currently configured for Binance and CoinDCX Futures. You can add more exchanges by updating the configuration files.

**Q: Can I run multiple bots simultaneously?**
A: Yes! The system supports multiple bots trading different pairs simultaneously.

**Q: Is authentication required?**
A: Not in the current version. JWT authentication is planned for future releases.

### Technical Questions

**Q: Why PostgreSQL instead of MySQL?**
A: PostgreSQL offers:
- Better JSON support (JSONB)
- Advanced indexing
- Full ACID compliance
- Better performance for complex queries
- Native UUID support

**Q: Why Zustand instead of Redux?**
A: Zustand is:
- Simpler API
- Less boilerplate
- Smaller bundle size
- Better TypeScript support
- Easier to learn

**Q: Can I use SQLite instead of PostgreSQL?**
A: Yes, for development:
```env
DATABASE_URL=sqlite+aiosqlite:///./scalper.db
```
But PostgreSQL is recommended for production.

**Q: How do I add a new exchange?**
A:
1. Update `config/bot-config.ts`:
```typescript
export const EXCHANGES = [
  { value: 'Binance', label: 'Binance' },
  { value: 'Kraken', label: 'Kraken' },  // New
];
```

2. Update `backend/app/models/bot.py`:
```python
class Exchange(str, enum.Enum):
    BINANCE = "Binance"
    KRAKEN = "Kraken"  # New
```

3. Implement exchange API integration in `backend/app/services/`

**Q: How do I customize the UI theme?**
A: Edit `app/globals.css`:
```css
:root {
  --primary: 210 100% 50%;  /* Blue */
  /* Change to your brand color */
}
```

### Deployment Questions

**Q: Can I deploy the frontend and backend separately?**
A: Yes! Frontend can be on Vercel, backend on AWS/Heroku/Railway.

**Q: What are the minimum server requirements?**
A:
- **Frontend**: Any Node.js hosting (Vercel, Netlify)
- **Backend**: 1GB RAM, 1 CPU core minimum
- **Database**: 512MB RAM for small scale

**Q: How much does it cost to run?**
A:
- Frontend (Vercel): Free tier available
- Backend (AWS t3.micro): ~$10/month
- Database (AWS RDS t3.micro): ~$15/month
- **Total**: ~$25/month for small scale

**Q: How do I enable HTTPS?**
A: Use reverse proxy (nginx) with Let's Encrypt certificate, or use AWS ALB with ACM certificate.

### Data & Backup

**Q: How do I backup the database?**
A:
```bash
# Backup
pg_dump scalper_bot > backup.sql

# Restore
psql scalper_bot < backup.sql
```

**Q: How long is activity log data kept?**
A: Indefinitely by default. Implement cleanup:
```sql
DELETE FROM activity_logs
WHERE timestamp < NOW() - INTERVAL '30 days';
```

**Q: Can I export my bot configurations?**
A: Yes, use the API:
```bash
curl http://localhost:8000/api/v1/bots/ > bots.json
```

---

## Support & Contributing

### Getting Help

- **Documentation**: This file
- **GitHub Issues**: https://github.com/yourusername/scalper/issues
- **Email**: support@example.com

### Contributing

We welcome contributions! See CONTRIBUTING.md for guidelines.

**Quick start**:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

---

**Last Updated**: 2024-01-01
**Version**: 1.0.0
**Author**: Anuj Saini (@anujsainicse)
