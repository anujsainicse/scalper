# 🤖 Trading Bot Platform

A comprehensive multi-bot trading platform for cryptocurrency trading with real-time monitoring, advanced configuration, and automated strategies. Built with Next.js 15, TypeScript, and modern UI components.

![Next.js](https://img.shields.io/badge/Next.js-15.5.6-black)
![React](https://img.shields.io/badge/React-19.1.0-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)
![Tailwind](https://img.shields.io/badge/Tailwind-4.x-38B2AC)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Overview

Trading Bot Platform is a full-stack application that enables traders to automate their cryptocurrency trading strategies using multiple bot types. The platform features a modern, responsive UI with real-time monitoring, comprehensive analytics, and seamless bot management.

## ✨ Key Features

### 🏠 Unified Dashboard
- **Homepage Overview**: Central hub displaying all bot types and performance metrics
- **Stats Cards**: Real-time tracking of total bots, PnL, and daily performance
- **Bot Type Selection**: Quick access to all available trading strategies
- **Quick Start Guide**: Step-by-step onboarding for new users

### 🤖 Multiple Bot Types

#### ⚡ Scalper Bot (Active)
Fast-paced trading for quick profits in volatile markets:
- Quick buy/sell execution
- Trailing stop-loss support
- Real-time price tracking
- Infinite loop trading mode
- Configurable profit targets

#### 📊 Grid Bot (Coming Soon)
Automated grid trading for range-bound markets:
- Configurable grid levels
- Arithmetic and geometric strategies
- Dynamic adjustment based on volatility
- Buy low, sell high automation

#### 💰 DCA Bot (Coming Soon)
Dollar-cost averaging for long-term strategies:
- Scheduled recurring investments
- Customizable intervals (hourly, daily, weekly)
- Smart entry timing
- Portfolio rebalancing

#### 📉 Dip Bot (Coming Soon)
Capitalize on price dips:
- Configurable dip thresholds
- Volume confirmation
- Multi-timeframe analysis
- Automatic recovery targets

#### 🚀 Momentum Bot (Coming Soon)
Trend-following with momentum indicators:
- RSI, MACD tracking
- Trend strength analysis
- Dynamic entry/exit signals
- Customizable thresholds

### 🎨 Modern UI/UX

#### Collapsible Sidebar Navigation
- **Default Collapsed**: Icon-only view for maximum screen space
- **Expandable**: Full labels and descriptions on demand
- **Active Indicators**: Gradient highlights for current bot
- **Home Navigation**: Quick access to dashboard overview

#### Dynamic Header
- **Context-Aware Title**: Shows current bot type
- **Gradient Themes**: Unique colors for each bot type
- **Real-Time Price Ticker**: Live cryptocurrency prices (BTC, ETH, SOL, BNB, DOGE)
- **Collapse Control**: Toggle sidebar from header
- **User Menu**: Profile, settings, and logout access

#### User Menu Dropdown
- **Profile Management**: View user information
- **Theme Selector**: Light/Dark mode toggle
- **Exchange Connect**: Manage exchange API keys
- **Telegram Integration**: Enable notifications
- **Quick Logout**: Secure session management

### 🔐 Authentication & Security
- **Supabase Auth**: Secure email/password and OAuth
- **Google Sign-In**: One-click authentication
- **Password Reset**: Email-based recovery flow
- **Protected Routes**: Middleware-based access control
- **Session Management**: Persistent login with JWT

### 📝 Bot Configuration (Scalper)
- **Ticker Selection**: Popular trading pairs dropdown
- **Exchange Selection**: Multiple exchange support
- **Order Types**: BUY or SELL first
- **Price Settings**: Buy/sell price configuration
- **Quantity Options**: Preset or custom amounts
- **Trailing Stop**: Optional percentage-based stops
- **Leverage Control**: Adjustable leverage settings
- **Real-time Validation**: Instant feedback on inputs

### 🎯 Active Bot Management
- **Grid Layout**: Responsive 1-3 column display
- **Status Indicators**: Visual ACTIVE/STOPPED states
- **PnL Tracking**: Color-coded profit/loss display
- **Individual Controls**: Start, stop, edit, delete
- **Bulk Actions**: Emergency stop all bots
- **Trade Statistics**: Count and performance metrics
- **Last Activity**: Relative time display

### 💹 Real-Time Market Data

#### Price Ticker (Header)
- **Live Cryptocurrency Prices**: BTC, ETH, SOL, BNB, DOGE displayed in header
- **Auto-refresh**: Prices update every 5 seconds automatically
- **Visual Indicators**: Green for price increase, red for decrease
- **Smart Formatting**: Appropriate decimal precision per cryptocurrency
- **Redis Integration**: Fetches data from Bybit spot market via Redis
- **Responsive Design**: Shows top 3 cryptos on mobile (BTC, ETH, SOL)
- **Theme Support**: Works seamlessly in light and dark modes
- **Loading States**: Skeleton animation while fetching data

### 📊 Activity Monitoring

#### Activity Logs
- **Multi-level Filtering**: INFO, SUCCESS, WARNING, ERROR, TELEGRAM
- **Auto-scroll Toggle**: Follow latest activity
- **CSV Export**: Download complete history
- **Color-coded Entries**: Visual log categorization
- **Timestamp Display**: Precise activity tracking
- **Infinite Scroll**: Handle thousands of entries

#### Orders Panel
- **Order History**: Complete order tracking
- **Status Display**: Pending, filled, cancelled
- **Price Information**: Entry and exit prices
- **Profit Calculation**: Per-order PnL

#### WebSocket Monitor
- **Real-time Connection**: Live market data
- **Connection Status**: Visual indicators
- **Data Streaming**: Tick-by-tick updates
- **Auto-reconnect**: Resilient connections

#### Analytics Dashboard
- **Performance Charts**: Visual profit tracking
- **Win Rate Analysis**: Success metrics
- **Trade Distribution**: Volume analysis
- **Historical Data**: Time-series performance

## 🏗️ Architecture

### Frontend Structure
```
app/
├── (dashboard)/              # Protected dashboard routes
│   ├── layout.tsx           # Dashboard layout with sidebar
│   ├── home/                # Homepage
│   ├── scalper/             # Scalper bot page
│   ├── grid/                # Grid bot page
│   ├── dca/                 # DCA bot page
│   ├── dip/                 # Dip bot page
│   └── momentum/            # Momentum bot page
├── auth/
│   ├── callback/            # OAuth callback handler
│   └── reset-password/      # Password reset page
├── login/                   # Login/signup page
├── layout.tsx               # Root layout
└── page.tsx                 # Root redirect

components/
├── layout/
│   └── Sidebar.tsx          # Navigation sidebar
├── ui/                      # shadcn/ui components
├── BotConfiguration.tsx     # Bot config form
├── ActiveBots.tsx           # Bot management grid
├── ActivityLog.tsx          # Activity logging
├── Orders.tsx               # Order history
├── WebSocketMonitor.tsx     # WebSocket status
├── UserMenu.tsx             # User dropdown menu
├── ProtectedRoute.tsx       # Auth guard
└── TelegramConnect.tsx      # Telegram integration

store/
└── botStore.ts              # Zustand state management

contexts/
├── AuthContext.tsx          # Authentication context
└── WebSocketContext.tsx     # WebSocket management

lib/
├── api.ts                   # API client
└── supabase/                # Supabase configuration

types/
└── bot.ts                   # TypeScript definitions

config/
└── bot-config.ts            # Configuration constants
```

### Backend API (FastAPI)
```
backend/
├── app/
│   ├── api/v1/
│   │   └── endpoints/
│   │       ├── auth.py      # Authentication
│   │       ├── bots.py      # Bot CRUD
│   │       ├── logs.py      # Activity logs
│   │       └── orders.py    # Order management
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   └── core/                # Config & DB
└── requirements.txt
```

### State Management

#### Zustand Store
```typescript
interface BotStore {
  // State
  bots: ActiveBot[]
  logs: ActivityLog[]
  editingBotId: string | null
  telegramConnected: boolean

  // Actions
  addBot: (formData: BotFormData) => Promise<void>
  removeBot: (id: string) => Promise<void>
  updateBot: (id: string, updates: Partial<ActiveBot>) => Promise<void>
  toggleBot: (id: string) => Promise<void>
  stopAllBots: () => Promise<void>
  addLog: (level: LogLevel, message: string) => void
  clearLogs: () => Promise<void>
}
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18.x or higher
- Python 3.11+ (for backend)
- PostgreSQL 15+
- Redis 7+

### Frontend Setup

1. **Clone the repository**
```bash
git clone https://github.com/anujsainicse/scalper.git
cd scalper
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
```

4. **Run development server**
```bash
npm run dev
```

5. **Open browser**
Navigate to [http://localhost:3000](http://localhost:3000)

### Backend Setup

1. **Navigate to backend**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/trading_bot
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
```

5. **Start server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access API docs**
Navigate to [http://localhost:8000/docs](http://localhost:8000/docs)

## 📚 Documentation

### API Endpoints

#### Authentication
```
POST   /api/v1/auth/register        # Register new user
POST   /api/v1/auth/login           # User login
POST   /api/v1/auth/refresh         # Refresh token
POST   /api/v1/auth/logout          # User logout
```

#### Bots
```
GET    /api/v1/bots                 # List all bots
POST   /api/v1/bots                 # Create bot
GET    /api/v1/bots/{id}            # Get bot details
PUT    /api/v1/bots/{id}            # Update bot
DELETE /api/v1/bots/{id}            # Delete bot
POST   /api/v1/bots/{id}/start      # Start bot
POST   /api/v1/bots/{id}/stop       # Stop bot
POST   /api/v1/bots/{id}/toggle     # Toggle status
POST   /api/v1/bots/stop-all        # Emergency stop
```

#### Activity Logs
```
GET    /api/v1/logs                 # Get logs
POST   /api/v1/logs                 # Create log
DELETE /api/v1/logs                 # Clear logs
GET    /api/v1/logs/count           # Log counts
```

### Configuration

#### Adding a New Exchange
Edit `config/bot-config.ts`:
```typescript
export const EXCHANGES: ConfigItem[] = [
  { value: 'CoinDCX F', label: 'CoinDCX F' },
  { value: 'Binance', label: 'Binance' },
  { value: 'Kraken', label: 'Kraken' }, // New exchange
];
```

#### Adding a New Ticker
```typescript
export const POPULAR_TICKERS = [
  'BTC/USDT',
  'ETH/USDT',
  'SOL/USDT', // New ticker
];
```

## 🎨 UI Components

### shadcn/ui Components Used
- `Button` - Actions and controls
- `Card` - Content containers
- `Input` - Form inputs
- `Select` - Dropdown menus
- `Checkbox` - Boolean toggles
- `RadioGroup` - Option selection
- `Alert` - Notifications and warnings
- `Badge` - Status indicators
- `DropdownMenu` - Context menus
- `Tabs` - Content organization

### Custom Components
- `BotConfiguration` - Bot creation form
- `ActiveBots` - Bot management grid
- `ActivityLog` - Log viewer with filters
- `Sidebar` - Collapsible navigation
- `UserMenu` - User dropdown
- `TelegramConnect` - Telegram modal

## 🔧 Development

### Code Style
- **TypeScript**: Strict mode enabled
- **ESLint**: Configured for Next.js
- **Prettier**: Code formatting
- **Conventions**: camelCase for variables, PascalCase for components

### Testing
```bash
# Run tests (when configured)
npm test

# Type checking
npm run type-check

# Linting
npm run lint
```

### Building for Production
```bash
# Build frontend
npm run build
npm start

# Build backend
# (Deploy with Docker or ASGI server)
```

## 🚢 Deployment

### Frontend (Vercel)
1. Connect GitHub repository
2. Configure environment variables
3. Deploy automatically on push

### Backend (Docker)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/) - React framework
- [shadcn/ui](https://ui.shadcn.com/) - UI components
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [Zustand](https://zustand-demo.pmnd.rs/) - State management
- [Supabase](https://supabase.com/) - Authentication
- [Lucide React](https://lucide.dev/) - Icons

## 📧 Contact

**Author**: Anuj Saini
**GitHub**: [@anujsainicse](https://github.com/anujsainicse)
**Repository**: [Trading Bot Platform](https://github.com/anujsainicse/scalper)

## 🗺️ Roadmap

### Phase 1: Core Platform ✅
- [x] Multi-bot architecture
- [x] Collapsible sidebar navigation
- [x] Homepage dashboard
- [x] User authentication
- [x] Scalper bot implementation

### Phase 2: Grid Bot
- [ ] Grid configuration UI
- [ ] Grid level management
- [ ] Arithmetic/Geometric strategies
- [ ] Real-time grid visualization

### Phase 3: DCA Bot
- [ ] Investment schedule configuration
- [ ] Interval-based buying
- [ ] Portfolio rebalancing
- [ ] Historical DCA analysis

### Phase 4: Dip Bot
- [ ] Dip detection algorithm
- [ ] Volume confirmation
- [ ] Multi-timeframe analysis
- [ ] Recovery target automation

### Phase 5: Momentum Bot
- [ ] Indicator integration (RSI, MACD)
- [ ] Trend detection
- [ ] Entry/exit signal generation
- [ ] Momentum scoring

### Phase 6: Advanced Features
- [ ] Backtesting engine
- [ ] Strategy optimization
- [ ] Portfolio analytics
- [ ] Risk management tools
- [ ] Paper trading mode

---

**Built with ❤️ by Anuj Saini**
