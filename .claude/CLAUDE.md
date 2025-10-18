# Scalper Bot - AI Development Guide

## Project Overview

Scalper Bot is a full-stack cryptocurrency trading bot management platform with real-time monitoring and automated trading capabilities.

**Project Type**: Full-stack web application (Next.js + FastAPI)
**Primary Use Case**: Cryptocurrency scalping bot configuration and monitoring
**Target Users**: Crypto traders who want to automate scalping strategies
**Development Status**: Active development, production-ready MVP

## Critical Information

### NEVER Do These Things
- ❌ Never commit `.env` files or expose API keys
- ❌ Never modify the database schema without creating migrations
- ❌ Never use `any` type in TypeScript - always use proper types
- ❌ Never bypass Pydantic validation in the backend
- ❌ Never hardcode configuration values - use config files
- ❌ Never use `console.log` in production code - use proper logging
- ❌ Never create new files without reading existing similar files first
- ❌ Never deploy without testing both frontend and backend

### ALWAYS Do These Things
- ✅ Always use TypeScript for all frontend code
- ✅ Always use async/await for database operations
- ✅ Always validate user inputs with Pydantic schemas
- ✅ Always use the existing component patterns (shadcn/ui)
- ✅ Always update the Zustand store for state changes
- ✅ Always add activity logs for important actions
- ✅ Always test API endpoints before pushing
- ✅ Always follow the existing file structure

## Technology Stack

### Frontend
```
Framework:       Next.js 15.5.6 (App Router)
Language:        TypeScript 5.x
UI Library:      shadcn/ui (Radix UI primitives)
Styling:         Tailwind CSS 3.4.1
State:           Zustand 5.0.2
Notifications:   react-hot-toast 2.4.1
Icons:           Lucide React 0.468.0
Theme:           next-themes 0.4.4
```

### Backend
```
Framework:       FastAPI 0.109.0
Language:        Python 3.9+
Database:        PostgreSQL 15+ (async)
ORM:             SQLAlchemy 2.0.25 (async)
Validation:      Pydantic 2.5.3
Server:          Uvicorn (ASGI)
Migrations:      Alembic 1.13.1
```

### Development Tools
```
Package Manager: npm
Python Env:      venv
Database Client: psql
API Testing:     curl, Swagger UI (http://localhost:8000/docs)
```

## Project Structure

```
scalper/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout with Toaster
│   ├── page.tsx                 # Main dashboard (3-panel layout)
│   └── globals.css              # Global styles + Tailwind
│
├── components/                   # React Components
│   ├── BotConfiguration.tsx     # Left panel - Bot creation form
│   ├── ActiveBots.tsx           # Middle panel - Bot grid with tabs
│   ├── ActivityLog.tsx          # Right panel - Activity logs with filters
│   ├── BotStatistics.tsx        # Statistics display (if needed)
│   ├── TelegramConnect.tsx      # Telegram connection button
│   ├── ThemeToggle.tsx          # Dark/light theme toggle
│   └── ui/                      # shadcn/ui components (DO NOT EDIT DIRECTLY)
│
├── store/                       # Zustand State Management
│   └── botStore.ts              # Global bot store (bots, logs, telegram)
│
├── types/                       # TypeScript Definitions
│   └── bot.ts                   # All type definitions
│
├── utils/                       # Utility Functions
│   ├── formatters.ts            # Format helpers (PnL, time, validation)
│   └── toast.tsx                # Custom dismissible toast utility
│
├── config/                      # Configuration Files
│   ├── bot-config.ts            # Dropdown options (exchanges, quantities, etc.)
│   └── README.md                # Config documentation
│
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── main.py              # FastAPI app with CORS
│   │   ├── api/v1/
│   │   │   ├── router.py        # API router
│   │   │   └── endpoints/
│   │   │       ├── bots.py      # Bot CRUD endpoints (10 endpoints)
│   │   │       └── logs.py      # Activity log endpoints (4 endpoints)
│   │   ├── core/
│   │   │   └── config.py        # Pydantic Settings
│   │   ├── db/
│   │   │   └── session.py       # Async database session
│   │   ├── models/
│   │   │   └── bot.py           # SQLAlchemy models (Bot, ActivityLog, Trade)
│   │   └── schemas/
│   │       └── bot.py           # Pydantic schemas for validation
│   ├── .env.example             # Environment variables template
│   ├── requirements.txt         # Python dependencies
│   └── README.md                # Backend setup guide
│
├── public/                      # Static assets
├── .env.local                   # Frontend environment (NEVER COMMIT)
├── backend/.env                 # Backend environment (NEVER COMMIT)
├── package.json                 # Node dependencies
├── tsconfig.json                # TypeScript config
├── tailwind.config.ts           # Tailwind config
└── next.config.ts               # Next.js config
```

## Architecture Patterns

### Frontend Architecture

#### Component Patterns
```typescript
// ALWAYS use this pattern for components:

'use client'; // Required for client components

import React, { useState } from 'react';
import { useBotStore } from '@/store/botStore';
import { Button } from './ui/button';

export const MyComponent: React.FC = () => {
  // 1. Get store actions and state
  const bots = useBotStore((state) => state.bots);
  const addBot = useBotStore((state) => state.addBot);

  // 2. Local state
  const [localState, setLocalState] = useState('');

  // 3. Event handlers
  const handleAction = async () => {
    try {
      await addBot(data);
      toast.success('Success');
    } catch (error) {
      toast.error('Error');
    }
  };

  // 4. Render
  return <div>...</div>;
};
```

#### State Management Pattern
```typescript
// ALWAYS update Zustand store for global state
// NEVER use local state for data that other components need

// ✅ CORRECT - Use store
const addBot = useBotStore((state) => state.addBot);
addBot(newBot);

// ❌ WRONG - Don't use local state for bots
const [bots, setBots] = useState([]);
```

#### Form Handling Pattern
```typescript
// ALWAYS use this pattern for forms:

const [formData, setFormData] = useState<FormType>({
  field1: defaultValue,
  field2: defaultValue,
});

const handleInputChange = (field: keyof FormType, value: any) => {
  setFormData((prev) => ({ ...prev, [field]: value }));
};

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!validateForm()) return;

  try {
    await submitAction(formData);
    toast.success('Success');
    resetForm();
  } catch (error) {
    toast.error('Error');
  }
};
```

### Backend Architecture

#### Endpoint Pattern
```python
# ALWAYS use this pattern for endpoints:

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.bot import Bot
from app.schemas.bot import BotCreate, BotResponse

router = APIRouter()

@router.post("/", response_model=BotResponse, status_code=201)
async def create_bot(
    bot_data: BotCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new bot
    """
    # 1. Create model instance
    bot = Bot(**bot_data.dict())

    # 2. Add to database
    db.add(bot)
    await db.flush()

    # 3. Create activity log
    log = ActivityLog(bot_id=bot.id, level="SUCCESS", message=f"Bot created")
    db.add(log)

    # 4. Commit
    await db.commit()
    await db.refresh(bot)

    # 5. Return response
    return bot
```

#### Database Query Pattern
```python
# ALWAYS use async/await with SQLAlchemy

# ✅ CORRECT
from sqlalchemy import select

result = await db.execute(select(Bot).where(Bot.id == bot_id))
bot = result.scalar_one_or_none()

if not bot:
    raise HTTPException(status_code=404, detail="Bot not found")

# ❌ WRONG - Don't use sync queries
bot = db.query(Bot).filter(Bot.id == bot_id).first()
```

## Key Files to Know

### Configuration Files

**`config/bot-config.ts`** - Central configuration
- Add exchanges here: `EXCHANGES`
- Add quantities here: `QUANTITIES`
- Add trailing percentages: `TRAILING_PERCENTAGES`
- Add popular tickers: `POPULAR_TICKERS`

**`backend/app/core/config.py`** - Backend configuration
- Environment variables
- CORS settings
- Database URL
- API settings

### State Management

**`store/botStore.ts`** - Global state
- `bots`: Array of all bots
- `logs`: Array of activity logs
- `editingBotId`: Currently editing bot ID
- `telegramConnected`: Telegram connection status

Actions:
- `addBot(formData)` - Create new bot
- `removeBot(id)` - Delete bot
- `updateBot(id, updates)` - Update bot fields
- `toggleBot(id)` - Toggle ACTIVE ↔ STOPPED
- `stopAllBots()` - Emergency stop
- `setEditingBot(id)` - Set bot for editing
- `addLog(level, message)` - Add activity log
- `clearLogs()` - Clear all logs
- `toggleTelegram()` - Toggle Telegram status

### Type Definitions

**`types/bot.ts`** - All TypeScript types
```typescript
type Exchange = 'CoinDCX F' | 'Binance';
type OrderSide = 'BUY' | 'SELL';
type BotStatus = 'ACTIVE' | 'STOPPED';
type LogLevel = 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR' | 'TELEGRAM';

interface BotFormData { ... }
interface ActiveBot { ... }
interface ActivityLog { ... }
```

### Database Models

**`backend/app/models/bot.py`** - SQLAlchemy models
- `Bot` - Main bot configuration
- `ActivityLog` - Activity logging
- `Trade` - Trade execution records

**Important**: Never use `metadata` as column name (reserved by SQLAlchemy)
Use `extra_data` instead.

## Common Development Tasks

### Adding a New Exchange

1. **Update frontend config** (`config/bot-config.ts`):
```typescript
export const EXCHANGES: ConfigItem[] = [
  { value: 'CoinDCX F', label: 'CoinDCX F' },
  { value: 'Binance', label: 'Binance' },
  { value: 'Kraken', label: 'Kraken' }, // NEW
];
```

2. **Update backend model** (`backend/app/models/bot.py`):
```python
class Exchange(str, enum.Enum):
    COINDCX_F = "CoinDCX F"
    BINANCE = "Binance"
    KRAKEN = "Kraken"  # NEW
```

3. **Update TypeScript types** (`types/bot.ts`):
```typescript
export type Exchange = 'CoinDCX F' | 'Binance' | 'Kraken'; // NEW
```

### Adding a New Component

1. **Create component file** in `components/`
2. **Follow the component pattern** (see above)
3. **Import and use** in `app/page.tsx`
4. **Update types** if needed in `types/bot.ts`

### Adding a New API Endpoint

1. **Create schema** in `backend/app/schemas/bot.py`
2. **Create endpoint** in `backend/app/api/v1/endpoints/bots.py` or new file
3. **Register router** in `backend/app/api/v1/router.py`
4. **Test** at http://localhost:8000/docs

### Modifying Database Schema

1. **Update model** in `backend/app/models/bot.py`
2. **Update schema** in `backend/app/schemas/bot.py`
3. **Create migration**: `alembic revision --autogenerate -m "description"`
4. **Apply migration**: `alembic upgrade head`
5. **Update TypeScript types** in `types/bot.ts`

## Code Style Guidelines

### TypeScript/React
- Use functional components with hooks
- Use `const` for components: `export const MyComponent: React.FC = () => {}`
- Always type props with interfaces
- Use destructuring for props and state
- Use template literals for strings with variables
- Use optional chaining: `bot?.ticker`
- Use nullish coalescing: `value ?? defaultValue`

### Python/FastAPI
- Follow PEP 8
- Use type hints everywhere
- Use async/await for all I/O operations
- Use Pydantic for validation
- Use descriptive variable names
- Use docstrings for all functions
- Use f-strings for string formatting

### Naming Conventions
- **Components**: PascalCase (`BotConfiguration.tsx`)
- **Functions**: camelCase (`handleSubmit`)
- **Constants**: UPPER_SNAKE_CASE (`POPULAR_TICKERS`)
- **Types**: PascalCase (`BotFormData`)
- **Interfaces**: PascalCase with descriptive names (`ActiveBot`)
- **Variables**: camelCase (`activeBots`)
- **CSS Classes**: kebab-case (Tailwind handles this)

## Testing Guidelines

### Frontend Testing (Manual)
1. Start dev server: `npm run dev`
2. Test in browser at http://localhost:3000
3. Check console for errors
4. Test all user flows
5. Test on different screen sizes

### Backend Testing
1. Visit http://localhost:8000/docs
2. Use "Try it out" for each endpoint
3. Test with curl:
```bash
# Create bot
curl -X POST "http://localhost:8000/api/v1/bots/" \
  -H "Content-Type: application/json" \
  -d '{"ticker":"BTC/USDT","exchange":"Binance",...}'

# Get bots
curl "http://localhost:8000/api/v1/bots/"
```

### Integration Testing
1. Create bot via UI
2. Check database: `psql scalper_bot`
3. Verify API response matches UI
4. Test all CRUD operations
5. Test edge cases (empty states, errors)

## Environment Setup

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://username@localhost:5432/scalper_bot
SECRET_KEY=your-secret-key-min-32-chars
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## Common Issues & Solutions

### Issue: Port already in use
```bash
# Find process
lsof -i :3000  # or :8000

# Kill process
kill -9 <PID>
```

### Issue: Database connection error
```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL
brew services start postgresql@15

# Check database exists
psql -l | grep scalper_bot
```

### Issue: Import errors in Python
```bash
# Activate venv
source backend/venv/bin/activate

# Reinstall deps
pip install -r backend/requirements.txt
```

### Issue: Next.js build errors
```bash
# Clear cache
rm -rf .next

# Reinstall deps
rm -rf node_modules package-lock.json
npm install

# Restart dev server
npm run dev
```

## Best Practices

### Performance
- Use React.memo() for expensive components
- Use useMemo() and useCallback() when needed
- Optimize database queries with indexes
- Use pagination for large datasets
- Lazy load heavy components

### Security
- Never commit `.env` files
- Validate all user inputs
- Use parameterized queries (SQLAlchemy does this)
- Sanitize error messages before showing to users
- Use HTTPS in production

### Code Organization
- Keep components under 300 lines
- Extract reusable logic into hooks or utils
- Group related files together
- Use barrel exports (index.ts) when needed
- Comment complex logic

### Git Workflow
- Create feature branches: `git checkout -b feature/feature-name`
- Commit often with clear messages
- Test before committing
- Never commit node_modules or venv
- Use .gitignore properly

## API Endpoints Reference

### Bots
```
GET    /api/v1/bots/                    # List all bots
POST   /api/v1/bots/                    # Create bot
GET    /api/v1/bots/{id}                # Get bot
PUT    /api/v1/bots/{id}                # Update bot
DELETE /api/v1/bots/{id}                # Delete bot
POST   /api/v1/bots/{id}/start          # Start bot
POST   /api/v1/bots/{id}/stop           # Stop bot
POST   /api/v1/bots/{id}/toggle         # Toggle status
POST   /api/v1/bots/stop-all            # Emergency stop
GET    /api/v1/bots/statistics/summary  # Get statistics
```

### Activity Logs
```
GET    /api/v1/logs/        # List logs
POST   /api/v1/logs/        # Create log
DELETE /api/v1/logs/        # Clear all logs
GET    /api/v1/logs/count   # Get counts
```

## Deployment Checklist

### Frontend (Vercel)
- [ ] Update `NEXT_PUBLIC_API_URL` to production API
- [ ] Test production build: `npm run build && npm start`
- [ ] Check for console errors
- [ ] Test on mobile devices
- [ ] Deploy: `vercel --prod`

### Backend (Docker/AWS)
- [ ] Set `DEBUG=False` in .env
- [ ] Update `SECRET_KEY` to secure random value
- [ ] Configure CORS for production domain
- [ ] Set up database backups
- [ ] Test all endpoints
- [ ] Monitor logs and errors

## Quick Commands

```bash
# Frontend
npm run dev              # Start dev server
npm run build            # Build for production
npm start                # Run production build
npm run lint             # Run linter

# Backend
cd backend
source venv/bin/activate # Activate venv
uvicorn app.main:app --reload  # Start dev server
pytest                   # Run tests
alembic upgrade head     # Apply migrations

# Database
psql scalper_bot         # Connect to database
psql -l                  # List databases
pg_dump scalper_bot > backup.sql  # Backup

# Git
git status               # Check status
git add .                # Stage changes
git commit -m "message"  # Commit
git push                 # Push to remote
```

## Important Notes

1. **Zustand Store is Source of Truth** - Always update store for state changes
2. **Always Use Types** - No `any` types in TypeScript
3. **Async/Await Everywhere** - All database operations must be async
4. **Activity Logs for Everything** - Log all important actions
5. **Toast Notifications** - Show user feedback for all actions
6. **Error Handling** - Try/catch all async operations
7. **Validation** - Validate on both frontend and backend
8. **CORS** - Backend configured for http://localhost:3000
9. **Hot Reload** - Both frontend and backend support hot reload
10. **Documentation** - Update docs when adding features

## Resources

- **Project Docs**: See `DOCS.md`, `README.md`, `API_REFERENCE.md`
- **Quick Start**: See `QUICK_START.md`
- **Component Docs**: See `README.md` in project root
- **Backend Docs**: See `backend/README.md`
- **Config Docs**: See `config/README.md`
- **API Docs**: http://localhost:8000/docs (when running)

## Contact & Support

- **Developer**: Anuj Saini (@anujsainicse)
- **Repository**: https://github.com/anujsainicse/scalper
- **Issues**: GitHub Issues
- **Email**: support@example.com

---

**Last Updated**: 2024-10-18
**Version**: 1.0.0
**AI Assistant**: Use this guide to understand the project structure and patterns
