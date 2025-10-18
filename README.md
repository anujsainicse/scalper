# 🤖 Scalper Bot Dashboard

A modern Next.js frontend application for managing cryptocurrency scalping bots with real-time monitoring, configuration, and comprehensive activity logging.

![Next.js](https://img.shields.io/badge/Next.js-15.5.6-black)
![React](https://img.shields.io/badge/React-19.1.0-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)
![Tailwind](https://img.shields.io/badge/Tailwind-4.x-38B2AC)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

### 📝 Bot Configuration Panel
Create and configure scalping bots with an intuitive form interface:
- **Ticker Selection**: Dropdown with popular trading pairs (BTC/USDT, ETH/USDT, etc.)
- **Exchange Selection**: Choose from multiple exchanges (CoinDCX F, Binance)
- **First Order Type**: Select BUY or SELL for initial order
- **Quantity Options**: Preset quantities (1, 2, 3, 5, 10) or custom amount
- **Price Configuration**: Set buy and sell prices with validation
- **Trailing Stop**: Optional trailing percentage (0.1%, 0.5%, 1%)
- **Infinite Loop**: Enable continuous automated trading
- **Edit Mode**: Update existing bot configurations seamlessly
- **Real-time Validation**: Instant feedback with grouped error alerts

### 🎯 Active Bots Management
Monitor and control all your bots with a responsive grid layout:
- **Responsive Grid**: 1 column (mobile), 2 columns (tablet), 3 columns (desktop)
- **Real-time Status**: Visual indicators for ACTIVE/STOPPED states
- **PnL Tracking**: Color-coded profit/loss with trending indicators
- **Individual Controls**: Start, Stop, Edit, or Delete each bot
- **Emergency Stop**: Stop all bots with one click (with confirmation)
- **Telegram Integration**: Connection status indicator with toggle
- **Last Fill Time**: Relative time display (e.g., "2 mins ago")
- **Trade Statistics**: Total trades count and performance metrics
- **Smart Delete**: Double-click confirmation to prevent accidents

### 📊 Activity Log System
Comprehensive logging with powerful filtering and export capabilities:
- **Multi-level Filtering**: ALL, INFO, SUCCESS, WARNING, ERROR, TELEGRAM
- **Auto-scroll**: Toggle automatic scrolling to latest logs
- **CSV Export**: Download complete activity history
- **Color-coded Entries**: Visual distinction by log level
- **Timestamp Display**: HH:MM:SS format for precise tracking
- **Clear Function**: Remove all logs with confirmation
- **Infinite Scroll**: Handle thousands of log entries efficiently

### ⚙️ Configuration System
Centralized configuration file for easy customization:
- **bot-config.ts**: Single file for all dropdown options
- **Exchanges**: Add/remove trading platforms
- **Quantities**: Customize trading amounts
- **Trailing Percentages**: Configure stop-loss options
- **Popular Tickers**: Pre-defined trading pairs
- **Comprehensive Documentation**: Detailed README in config folder

## 🚀 Tech Stack

| Category | Technology |
|----------|-----------|
| **Framework** | Next.js 15.5.6 with App Router & Turbopack |
| **Language** | TypeScript 5.x |
| **UI Library** | shadcn/ui (Radix UI primitives) |
| **Styling** | Tailwind CSS 4.x |
| **State Management** | Zustand 5.0.8 |
| **Icons** | Lucide React 0.546.0 |
| **Notifications** | React Hot Toast 2.6.0 |
| **Date Utilities** | date-fns 4.1.0 |
| **Theme** | next-themes 0.4.6 |
| **Utilities** | clsx, tailwind-merge, CVA |

## 📦 Installation

### Prerequisites
- **Node.js** 18.x or higher
- **npm** (comes with Node.js)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/scalper.git
cd scalper
```

2. **Install dependencies**
```bash
npm install
```

3. **Run development server**
```bash
npm run dev
```

4. **Open in browser**
Navigate to [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
scalper/
├── app/
│   ├── page.tsx              # Main dashboard (3-panel layout)
│   ├── layout.tsx            # Root layout with metadata
│   ├── globals.css           # Global styles & Tailwind config
│   └── favicon.ico           # App icon
│
├── components/
│   ├── BotConfiguration.tsx  # Bot creation/edit form
│   ├── ActiveBots.tsx        # Bot grid display with controls
│   ├── ActivityLog.tsx       # Logging panel with filters
│   └── ui/                   # shadcn/ui components
│       ├── alert.tsx         # Alert component
│       ├── badge.tsx         # Badge component
│       ├── button.tsx        # Button component
│       ├── card.tsx          # Card component
│       ├── checkbox.tsx      # Checkbox component
│       ├── input.tsx         # Input component
│       ├── label.tsx         # Label component
│       ├── radio-group.tsx   # Radio group component
│       └── select.tsx        # Select dropdown component
│
├── store/
│   └── botStore.ts           # Zustand state management
│
├── types/
│   └── bot.ts                # TypeScript interfaces & types
│
├── utils/
│   └── formatters.ts         # Utility functions (format, validate)
│
├── config/
│   ├── bot-config.ts         # Centralized configuration
│   └── README.md             # Configuration guide
│
├── components.json           # shadcn/ui configuration
├── tailwind.config.ts        # Tailwind configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Project dependencies
```

## 🎮 Usage Guide

### Creating a Bot

1. **Fill in Bot Configuration Form**:
   - **Ticker**: Select from dropdown (BTC/USDT, ETH/USDT, etc.)
   - **Exchange**: Choose your trading platform
   - **First Order**: Select BUY or SELL
   - **Quantity**: Choose preset or custom amount
   - **Buy Price**: Enter buy price (must be > 0)
   - **Sell Price**: Enter sell price (must be > buy price)
   - **Trailing %**: Optional (0.1% to 3%)
   - **Infinite Loop**: Check for continuous trading

2. **Click "Start Bot"**:
   - Bot is created in ACTIVE state immediately
   - Activity log records the action
   - Bot appears in the Active Bots grid

### Managing Bots

#### Individual Bot Actions
- **Start/Stop**: Toggle bot activity state
- **Edit**: Load bot settings into configuration form
  - Form changes to "Update Bot" mode
  - Cancel button appears
  - Make changes and click "Update Bot"
- **Delete**: Click once, then confirm by clicking again

#### Bulk Actions
- **Stop All Bots**: Emergency stop button (with confirmation)
- **Telegram Toggle**: Simulate connection status

#### Bot Card Information
Each bot card displays:
- Ticker symbol and exchange
- Current status (ACTIVE/STOPPED)
- Buy and sell prices
- Trading quantity
- Last fill time (relative)
- Profit/Loss (PnL) with trend indicator
- Total trades executed

### Activity Logs

#### Filtering
- Click tabs to filter by level: **ALL**, **INFO**, **SUCCESS**, **WARNING**, **ERROR**, **TELEGRAM**
- Active filter is highlighted
- Counter badge shows entries per level

#### Features
- **Auto-scroll**: Toggle to automatically scroll to newest logs
- **Export CSV**: Download complete log history
- **Clear Logs**: Remove all entries (with confirmation)

## 🔧 Customization

### Adding Exchanges

Edit `config/bot-config.ts`:

```typescript
export const EXCHANGES: ConfigItem[] = [
  { value: 'CoinDCX F', label: 'CoinDCX F' },
  { value: 'Binance', label: 'Binance' },
  { value: 'Kraken', label: 'Kraken' },        // New exchange
  { value: 'Coinbase', label: 'Coinbase' },    // New exchange
];
```

### Adding Quantities

Edit `config/bot-config.ts`:

```typescript
export const QUANTITIES: ConfigItem[] = [
  { value: 1, label: '1' },
  { value: 5, label: '5' },
  { value: 10, label: '10' },
  { value: 25, label: '25' },      // New quantity
  { value: 50, label: '50' },      // New quantity
  { value: 0, label: 'Custom' },   // Keep for custom input
];
```

### Adding Trailing Percentages

Edit `config/bot-config.ts`:

```typescript
export const TRAILING_PERCENTAGES: ConfigItem[] = [
  { value: 'none', label: 'None' },      // Required
  { value: '0.1', label: '0.1%' },
  { value: '0.5', label: '0.5%' },
  { value: '1', label: '1%' },
  { value: '2', label: '2%' },           // New percentage
  { value: '3', label: '3%' },           // New percentage
];
```

### Adding Tickers

Edit `config/bot-config.ts`:

```typescript
export const POPULAR_TICKERS: string[] = [
  'BTC/USDT',
  'ETH/USDT',
  'SOL/USDT',
  'LINK/USDT',    // New ticker
  'UNI/USDT',     // New ticker
];
```

### Theme Colors

Edit `app/globals.css`:

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 240 10% 3.9%;
    --card: 0 0% 100%;
    --card-foreground: 240 10% 3.9%;
    /* ... more CSS variables */
  }

  .dark {
    --background: 240 10% 3.9%;
    --foreground: 0 0% 98%;
    --card: 240 10% 3.9%;
    --card-foreground: 0 0% 98%;
    /* ... more CSS variables */
  }
}
```

## 🏗️ Building for Production

```bash
# Build the application
npm run build

# Start production server
npm start
```

The optimized build output will be in the `.next` directory.

## 🧩 Key Components

### BotConfiguration (`components/BotConfiguration.tsx`)
- Form with real-time validation
- Create and edit bot configurations
- Dynamic form fields (custom quantity toggle)
- Error grouping and display
- Integration with Zustand store
- Cancel edit mode functionality

**Key Features**:
- Dropdown selections for all major fields
- Validation before submission
- Edit mode with pre-filled values
- Success/error toast notifications

### ActiveBots (`components/ActiveBots.tsx`)
- Responsive grid layout (1/2/3 columns)
- Individual bot cards with full controls
- Emergency stop all functionality
- Telegram connection indicator
- Delete confirmation pattern (double-click)
- Edit button for configuration updates

**Key Features**:
- Real-time status updates
- PnL visualization with trend indicators
- Last fill time with relative formatting
- Infinite loop indicator badge

### ActivityLog (`components/ActivityLog.tsx`)
- Tab-based filtering by log level
- Auto-scroll toggle for real-time monitoring
- CSV export functionality
- Color-coded entries by severity
- Timestamp formatting (HH:MM:SS)
- Clear all with confirmation

**Key Features**:
- Filter by: ALL, INFO, SUCCESS, WARNING, ERROR, TELEGRAM
- Counter badges showing entries per level
- Optimized rendering for large datasets

### Zustand Store (`store/botStore.ts`)
Centralized state management with the following actions:

**Bot Actions**:
- `addBot`: Create new bot (ACTIVE by default)
- `removeBot`: Delete bot with logging
- `updateBot`: Update specific bot properties
- `updateBotFromForm`: Update from form data
- `toggleBot`: Switch between ACTIVE/STOPPED
- `stopAllBots`: Emergency stop all bots
- `setEditingBot`: Set bot for editing

**Log Actions**:
- `addLog`: Add new activity log entry
- `clearLogs`: Remove all logs

**Other**:
- `toggleTelegram`: Toggle Telegram connection status

## 📋 Form Validation

The bot configuration form validates:

| Field | Rules |
|-------|-------|
| **Ticker** | Must match format: `XXX/XXX` (e.g., BTC/USDT) |
| **Exchange** | Required, must be from dropdown |
| **Quantity** | Must be > 0 (when custom) |
| **Buy Price** | Must be > 0 |
| **Sell Price** | Must be > buy price |
| **Trailing %** | Must be between 0.1% and 3% (if set) |

Validation errors are displayed in a grouped alert above the submit button.

## 🎨 UI/UX Features

### Responsive Design
- **Mobile** (< 768px): Single column, stacked panels
- **Tablet** (768px - 1280px): 2-column bot grid
- **Desktop** (> 1280px): 3-column bot grid, full layout

### Dark Theme
- Built with dark-first approach
- Consistent color scheme throughout
- High contrast for readability
- Custom scrollbar styling

### Accessibility
- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Focus indicators

### User Feedback
- Toast notifications for all actions
- Color-coded status indicators
- Loading states (where applicable)
- Confirmation dialogs for destructive actions

## 🔄 State Management Flow

```
User Action → Component Event Handler → Zustand Action
                                             ↓
                                    Update Store State
                                             ↓
                                    Trigger Re-render
                                             ↓
                           Update UI + Add Activity Log
                                             ↓
                                  Show Toast Notification
```

## 📝 Type Definitions

### Core Types (`types/bot.ts`)

```typescript
export type Exchange = 'CoinDCX F' | 'Binance';
export type OrderSide = 'BUY' | 'SELL';
export type BotStatus = 'ACTIVE' | 'STOPPED';
export type LogLevel = 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR' | 'TELEGRAM';

export interface BotFormData {
  ticker: string;
  exchange: Exchange;
  firstOrder: OrderSide;
  quantity: number;
  customQuantity?: number;
  buyPrice: number;
  sellPrice: number;
  trailingPercent?: number;
  infiniteLoop: boolean;
}

export interface ActiveBot extends BotConfig {
  id: string;
  status: BotStatus;
  pnl: number;
  totalTrades: number;
  lastFillTime?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface ActivityLog {
  id: string;
  timestamp: Date;
  level: LogLevel;
  message: string;
  botId?: string;
}
```

## 🚀 Future Enhancements

### Backend Integration
- [ ] Connect to real trading API
- [ ] WebSocket for live price updates
- [ ] Historical trade data persistence
- [ ] User authentication & authorization

### Analytics & Reporting
- [ ] Performance dashboard with charts
- [ ] Profit/loss graphs over time
- [ ] Win rate statistics
- [ ] Risk metrics visualization

### Advanced Features
- [ ] Bot templates for quick setup
- [ ] Import/Export configurations (JSON)
- [ ] Multi-bot strategy coordination
- [ ] Advanced risk management rules
- [ ] Backtesting with historical data
- [ ] Paper trading mode

### UI/UX Improvements
- [ ] Light/Dark theme toggle
- [ ] Multi-language support (i18n)
- [ ] Bot scheduling (time-based activation)
- [ ] Keyboard shortcuts
- [ ] Customizable dashboard layout
- [ ] Mobile app (React Native)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Anuj Saini**
- GitHub: [@anujsainicse](https://github.com/anujsainicse)

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/) - The React Framework
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful UI components
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Zustand](https://zustand-demo.pmnd.rs/) - State management
- [Lucide](https://lucide.dev/) - Beautiful icons
- [Radix UI](https://www.radix-ui.com/) - Unstyled, accessible components

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on [GitHub Issues](https://github.com/yourusername/scalper/issues)
- Email: your.email@example.com

---

**⚠️ Disclaimer**: This is a demo/educational project. Use at your own risk. Always test thoroughly before using real funds in cryptocurrency trading.

Made with ❤️ by Anuj Saini
