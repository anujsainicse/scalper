# Trading Bot Platform - Architecture Documentation

## 🏗️ System Architecture

### Overview
Trading Bot Platform is built using a modern full-stack architecture with Next.js frontend and FastAPI backend, designed for scalability, maintainability, and real-time performance.

## Frontend Architecture

### Technology Stack
- **Framework**: Next.js 15.5.6 (App Router)
- **Language**: TypeScript 5.x
- **UI Library**: shadcn/ui (Radix UI primitives)
- **Styling**: Tailwind CSS 4.x
- **State Management**: Zustand 5.0.8
- **HTTP Client**: Native Fetch API
- **Auth**: Supabase Auth
- **Real-time**: WebSocket API

### Directory Structure

```
app/
├── (dashboard)/                    # Route group for authenticated pages
│   ├── layout.tsx                 # Dashboard layout with sidebar & header
│   ├── home/page.tsx              # Homepage with bot overview
│   ├── scalper/page.tsx           # Scalper bot interface
│   ├── grid/page.tsx              # Grid bot interface (coming soon)
│   ├── dca/page.tsx               # DCA bot interface (coming soon)
│   ├── dip/page.tsx               # Dip bot interface (coming soon)
│   └── momentum/page.tsx          # Momentum bot interface (coming soon)
├── auth/
│   ├── callback/route.ts          # OAuth callback handler
│   └── reset-password/page.tsx    # Password reset page
├── login/page.tsx                 # Login/signup page
├── layout.tsx                     # Root layout (theme, auth providers)
├── page.tsx                       # Root redirect handler
└── globals.css                    # Global styles + Tailwind imports

components/
├── layout/
│   └── Sidebar.tsx                # Collapsible navigation sidebar
├── ui/                            # shadcn/ui components (auto-generated)
│   ├── button.tsx
│   ├── card.tsx
│   ├── dropdown-menu.tsx
│   ├── input.tsx
│   ├── select.tsx
│   └── ...
├── BotConfiguration.tsx           # Bot creation/edit form
├── ActiveBots.tsx                 # Bot grid with controls
├── ActivityLog.tsx                # Activity log viewer
├── Orders.tsx                     # Order history table
├── WebSocketMonitor.tsx           # WebSocket connection status
├── AnalyticsDashboard.tsx         # Performance analytics
├── UserMenu.tsx                   # User dropdown menu
├── ProtectedRoute.tsx             # Auth guard wrapper
├── TelegramConnect.tsx            # Telegram integration modal
├── ThemeToggle.tsx                # Theme switcher
├── ThemeProvider.tsx              # Theme context provider
└── DataLoader.tsx                 # Data initialization wrapper

contexts/
├── AuthContext.tsx                # Authentication state & methods
└── WebSocketContext.tsx           # WebSocket connection management

store/
└── botStore.ts                    # Zustand store for bot state

lib/
├── api.ts                         # API client with error handling
├── utils.ts                       # Utility functions (cn, etc.)
└── supabase/
    ├── client.ts                  # Supabase client instance
    └── server.ts                  # Server-side Supabase client

types/
└── bot.ts                         # TypeScript type definitions

config/
└── bot-config.ts                  # Configuration constants

utils/
├── formatters.ts                  # Format helpers
└── toast.tsx                      # Toast notification utility

middleware.ts                      # Auth middleware for route protection
```

### State Management

#### Zustand Store Pattern
```typescript
// store/botStore.ts
import { create } from 'zustand'

interface BotStore {
  // State
  bots: ActiveBot[]
  logs: ActivityLog[]
  editingBotId: string | null
  telegramConnected: boolean

  // Bot Actions
  addBot: (formData: BotFormData) => Promise<void>
  removeBot: (id: string) => Promise<void>
  updateBot: (id: string, updates: Partial<ActiveBot>) => Promise<void>
  updateBotFromForm: (id: string, formData: BotFormData) => Promise<void>
  toggleBot: (id: string) => Promise<void>
  stopAllBots: () => Promise<void>
  setEditingBot: (id: string | null) => void

  // Log Actions
  addLog: (level: LogLevel, message: string, botId?: string) => void
  clearLogs: () => Promise<void>

  // Telegram Actions
  toggleTelegram: () => void

  // Data Loading
  loadBots: () => Promise<void>
  loadLogs: () => Promise<void>
}
```

### Authentication Flow

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ 1. Visit /
       ▼
┌─────────────────┐
│  middleware.ts  │
└────────┬────────┘
         │
         │ 2. Check auth
         ▼
    ┌────────┐
    │ User?  │
    └───┬────┘
        │
    ┌───┴────┐
    │        │
   Yes       No
    │        │
    ▼        ▼
 /home    /login
```

### Component Architecture

#### Layout Hierarchy
```
RootLayout (app/layout.tsx)
├── ThemeProvider
├── AuthProvider
│   ├── ApiInitializer
│   │   └── WebSocketProvider
│   │       ├── Toaster
│   │       └── Page Content
```

#### Dashboard Layout
```
DashboardLayout (app/(dashboard)/layout.tsx)
├── Sidebar (collapsible)
│   ├── Home button
│   └── Bot type buttons
├── Header
│   ├── Collapse toggle
│   ├── Dynamic title
│   └── UserMenu
└── Main content area
    └── Page-specific content
```

### Routing Strategy

#### Route Groups
- `(dashboard)`: Protected routes requiring authentication
- Default: Public routes (login, auth callbacks)

#### Route Protection
```typescript
// middleware.ts
export async function middleware(request: NextRequest) {
  const supabase = createServerClient()
  const { data: { user } } = await supabase.auth.getUser()

  // Redirect logic based on user state and path
  if (!user && isProtectedRoute) {
    return NextResponse.redirect('/login')
  }

  if (user && isAuthRoute) {
    return NextResponse.redirect('/home')
  }
}
```

## Backend Architecture

### Technology Stack
- **Framework**: FastAPI 0.109.0
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+ (asyncpg driver)
- **ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic 2.5.3
- **Cache**: Redis 7
- **Server**: Uvicorn (ASGI)
- **Auth**: Supabase Auth (JWT verification)

### Directory Structure
```
backend/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── api/
│   │   └── v1/
│   │       ├── router.py          # API router
│   │       └── endpoints/
│   │           ├── auth.py        # Authentication endpoints
│   │           ├── bots.py        # Bot CRUD operations
│   │           ├── logs.py        # Activity logging
│   │           ├── orders.py      # Order management
│   │           └── telegram.py    # Telegram integration
│   ├── core/
│   │   ├── config.py              # Pydantic settings
│   │   ├── redis.py               # Redis connection
│   │   └── database.py            # Database config
│   ├── db/
│   │   └── session.py             # Async database session
│   ├── models/
│   │   ├── user.py                # User model
│   │   ├── bot.py                 # Bot model
│   │   ├── trade.py               # Trade model
│   │   ├── order.py               # Order model
│   │   └── activity_log.py        # Activity log model
│   ├── schemas/
│   │   ├── user.py                # User schemas
│   │   ├── bot.py                 # Bot schemas
│   │   ├── trade.py               # Trade schemas
│   │   └── order.py               # Order schemas
│   ├── services/
│   │   ├── auth.py                # Auth service
│   │   ├── encryption.py          # Encryption utilities
│   │   └── supabase_auth.py       # Supabase integration
│   └── dependencies/
│       └── auth.py                # Auth dependencies
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
└── README.md
```

### Database Schema

#### Entity Relationship Diagram
```
┌──────────────┐
│    users     │
└──────┬───────┘
       │ 1
       │
       │ n
┌──────┴───────┐
│     bots     │
└──────┬───────┘
       │ 1
       ├──────────────┐
       │              │
       │ n            │ n
┌──────┴───────┐ ┌───┴──────────┐
│    trades    │ │ activity_logs│
└──────┬───────┘ └──────────────┘
       │ 1
       │
       │ n
┌──────┴───────┐
│    orders    │
└──────────────┘
```

#### Key Models

**Users**
- id: UUID (Primary Key)
- email: VARCHAR(255) (Unique)
- supabase_user_id: UUID (Unique)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

**Bots**
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key → users)
- bot_type: ENUM (scalper, grid, dca, dip, momentum)
- ticker: VARCHAR(20)
- exchange: ENUM
- status: ENUM (ACTIVE, STOPPED, ERROR)
- config: JSONB (bot-specific configuration)
- pnl: DECIMAL
- total_trades: INTEGER
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

**Trades**
- id: UUID (Primary Key)
- bot_id: UUID (Foreign Key → bots)
- symbol: VARCHAR(20)
- side: ENUM (BUY, SELL)
- quantity: DECIMAL
- price: DECIMAL
- pnl: DECIMAL
- executed_at: TIMESTAMP

**Activity Logs**
- id: UUID (Primary Key)
- bot_id: UUID (Foreign Key → bots, nullable)
- level: ENUM (INFO, SUCCESS, WARNING, ERROR, TELEGRAM)
- message: VARCHAR(500)
- timestamp: TIMESTAMP
- extra_data: JSONB

### API Design

#### RESTful Principles
- Resource-based URLs
- HTTP methods for CRUD operations
- Proper status codes
- JSON responses
- Pagination for list endpoints

#### Authentication
```python
# JWT verification with Supabase
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    # Verify JWT token with Supabase
    # Fetch user from database
    # Return user object
```

#### Error Handling
```python
# Standardized error responses
{
    "detail": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input",
        "field": "price",
        "value": -100
    }
}
```

## Real-time Communication

### WebSocket Architecture
```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client  │◄────────┤   Next   │◄────────┤  Exchange│
│ (Browser)│         │    API   │         │   API    │
└──────────┘         └──────────┘         └──────────┘
     │                     │                     │
     │ WS Connection       │ HTTP Polling        │
     │                     │                     │
     ▼                     ▼                     ▼
┌──────────┐         ┌──────────┐         ┌──────────┐
│   Bot    │         │  Redis   │         │  Market  │
│  Updates │         │  Cache   │         │   Data   │
└──────────┘         └──────────┘         └──────────┘
```

## Security Architecture

### Authentication Layers
1. **Frontend**: Supabase Auth client
2. **Middleware**: Route protection
3. **Backend**: JWT verification
4. **Database**: Row-level security (future)

### Data Protection
- **Passwords**: Supabase Auth (bcrypt)
- **API Keys**: Fernet encryption at rest
- **Tokens**: HTTP-only cookies
- **CORS**: Configured for specific origins

## Performance Optimization

### Frontend Optimizations
- **Code Splitting**: Automatic with Next.js App Router
- **Image Optimization**: Next.js Image component
- **CSS**: Tailwind JIT compiler
- **State**: Zustand (lightweight, no re-renders)
- **Lazy Loading**: Dynamic imports for heavy components

### Backend Optimizations
- **Database**: Async SQLAlchemy for non-blocking I/O
- **Caching**: Redis for frequently accessed data
- **Connection Pooling**: PostgreSQL connection pool
- **Query Optimization**: Indexes on frequently queried columns

## Deployment Architecture

### Production Stack
```
┌─────────────────┐
│     Vercel      │ (Frontend)
└────────┬────────┘
         │
         │ HTTPS
         ▼
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
         ├──────────┬──────────┐
         ▼          ▼          ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│FastAPI #1│  │FastAPI #2│  │FastAPI #3│
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │            │            │
     └────────────┴────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
    ┌─────────┐      ┌─────────┐
    │PostgreSQL│      │  Redis  │
    └─────────┘      └─────────┘
```

## Scalability Considerations

### Horizontal Scaling
- **Frontend**: Edge deployment (Vercel)
- **Backend**: Multiple FastAPI instances
- **Database**: Read replicas
- **Cache**: Redis cluster

### Vertical Scaling
- **Database**: Upgraded instance size
- **Backend**: Increased worker processes
- **Cache**: Increased memory allocation

## Monitoring & Observability

### Logging Strategy
- **Frontend**: Console logs (development), Sentry (production)
- **Backend**: Structured logging with correlation IDs
- **Database**: Query logging for slow queries
- **WebSocket**: Connection lifecycle logging

### Metrics
- Request latency (p50, p95, p99)
- Error rates
- Active connections
- Database query performance
- Cache hit rates

## Future Enhancements

### Architecture Improvements
1. **Microservices**: Separate bot engines into individual services
2. **Event Sourcing**: Track all bot state changes
3. **CQRS**: Separate read and write models
4. **GraphQL**: Alternative API layer for complex queries
5. **gRPC**: High-performance internal communication

### Infrastructure
1. **Kubernetes**: Container orchestration
2. **Service Mesh**: Istio for advanced traffic management
3. **Message Queue**: RabbitMQ/Kafka for async processing
4. **CDN**: CloudFlare for static assets
5. **Monitoring**: Prometheus + Grafana

---

**Last Updated**: January 2025
**Version**: 1.0.0
