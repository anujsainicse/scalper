# Changelog

All notable changes to the Scalper Bot Dashboard project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-18

### Added

#### Core Features
- **Bot Configuration Panel**: Intuitive form for creating and configuring scalping bots
  - Ticker dropdown with popular cryptocurrency pairs (BTC/USDT, ETH/USDT, etc.)
  - Exchange selection (CoinDCX F, Binance)
  - First order type selection (BUY/SELL)
  - Quantity configuration with preset and custom options
  - Buy and sell price inputs with validation
  - Trailing stop percentage (optional, 0.1% to 3%)
  - Infinite loop mode toggle
  - Real-time form validation with grouped error alerts

- **Active Bots Management**: Comprehensive bot monitoring and control system
  - Responsive grid layout (1/2/3 columns based on screen size)
  - Individual bot cards showing:
    - Ticker symbol and exchange
    - Current status (ACTIVE/STOPPED) with color-coded badges
    - Buy and sell prices
    - Trading quantity
    - Last fill time (relative format: "2 mins ago")
    - Profit/Loss (PnL) with color coding and trend indicators
    - Total trades executed
  - Control buttons for each bot:
    - Start/Stop toggle
    - Edit (loads configuration for updating)
    - Delete (with double-click confirmation)
  - Emergency "Stop All Bots" button (with confirmation dialog)
  - Telegram connection status indicator with toggle
  - Trailing percentage and infinite loop badges

- **Activity Log System**: Comprehensive logging with filtering
  - Multi-level filtering tabs (ALL, INFO, SUCCESS, WARNING, ERROR, TELEGRAM)
  - Counter badges showing entries per level
  - Color-coded log entries by severity
  - Timestamp display (HH:MM:SS format)
  - Auto-scroll toggle for real-time monitoring
  - CSV export functionality
  - Clear all logs with confirmation
  - Optimized for handling thousands of log entries

- **Edit Bot Functionality**: Update existing bot configurations
  - Edit button on each bot card
  - Form pre-fills with existing bot data
  - "Update Bot" button replaces "Start Bot" in edit mode
  - Cancel button to exit edit mode
  - All changes logged in activity log
  - Toast notifications for successful updates

- **Configuration System**: Centralized configuration management
  - `config/bot-config.ts` file for all dropdown options
  - Configurable exchanges list
  - Customizable quantity options
  - Adjustable trailing percentages
  - Popular tickers list
  - Comprehensive documentation in `config/README.md`

#### UI/UX Enhancements
- **shadcn/ui Integration**: Modern, accessible component library
  - Alert component for validation errors
  - Badge component for status indicators
  - Button component with multiple variants
  - Card component for layouts
  - Checkbox component
  - Input component
  - Label component
  - Radio group component
  - Select dropdown component

- **Icons**: Lucide React icon library
  - Rocket icon for Start Bot
  - Play/Square icons for Start/Stop
  - Edit icon for editing bots
  - Trash icon for deletion
  - Alert icons for warnings
  - Trending up/down icons for PnL
  - Activity icon for bot status
  - Radio icon for Telegram connection

- **Toast Notifications**: React Hot Toast integration
  - Success messages for bot creation/updates
  - Warning messages for bot stops
  - Error messages for validation failures
  - Info messages for Telegram status

- **Dark Theme**: Complete dark mode styling
  - Consistent color scheme
  - High contrast for readability
  - Custom scrollbar styling
  - Hover states and transitions

- **Responsive Design**: Mobile-first approach
  - Mobile (< 768px): Single column layout
  - Tablet (768px - 1280px): 2-column bot grid
  - Desktop (> 1280px): 3-column bot grid
  - Stacked panels on small screens
  - Touch-friendly controls

#### State Management
- **Zustand Store**: Centralized state management
  - Bot state management (bots array)
  - Activity logs state (activityLogs array)
  - Telegram connection state
  - Editing bot ID state

- **Bot Actions**:
  - `addBot`: Create new bot (ACTIVE by default)
  - `removeBot`: Delete bot with logging
  - `updateBot`: Update specific bot properties
  - `updateBotFromForm`: Update from form data
  - `toggleBot`: Switch between ACTIVE/STOPPED
  - `stopAllBots`: Emergency stop all bots
  - `setEditingBot`: Set bot for editing

- **Log Actions**:
  - `addLog`: Add new activity log entry
  - `clearLogs`: Remove all logs

- **Other Actions**:
  - `toggleTelegram`: Toggle Telegram connection

#### Type Safety
- **TypeScript Types**: Comprehensive type definitions
  - `Exchange`: Union type for exchanges
  - `OrderSide`: Union type for BUY/SELL
  - `BotStatus`: Union type for ACTIVE/STOPPED
  - `LogLevel`: Union type for log levels
  - `BotFormData`: Interface for form data
  - `BotConfig`: Interface for bot configuration
  - `ActiveBot`: Interface for active bot state
  - `ActivityLog`: Interface for log entries
  - `ConfigItem`: Interface for configuration items

#### Validation
- **Form Validation**: Comprehensive input validation
  - Ticker format validation (XXX/XXX pattern)
  - Buy price > 0
  - Sell price > buy price
  - Custom quantity > 0 (when selected)
  - Trailing percentage between 0.1% and 3%
  - All validations with descriptive error messages
  - Errors displayed in grouped alert above submit button

#### Utilities
- **Formatters**: Utility functions
  - `formatRelativeTime`: Convert dates to relative format
  - `formatPnL`: Format profit/loss with color coding
  - `formatTimestamp`: Format timestamps (HH:MM:SS)
  - `generateId`: Generate unique IDs
  - `validateTicker`: Validate ticker format

#### Developer Experience
- **Next.js 15.5.6**: Latest framework features
  - App Router architecture
  - Turbopack for faster builds
  - Server and client components
  - Optimized bundle size

- **TypeScript 5.x**: Full type safety
  - Strict mode enabled
  - Path aliases (@/ for root)
  - Type inference
  - IntelliSense support

- **Tailwind CSS 4.x**: Modern utility-first CSS
  - Custom design tokens
  - Responsive breakpoints
  - Dark mode support
  - Custom animations

### Changed
- **Bot Creation Behavior**: Bots now start in ACTIVE state by default (previously STOPPED)
- **Success Log Level**: Bot creation logs use SUCCESS level instead of INFO
- **Ticker Input**: Changed from text input to dropdown with popular tickers
- **Bot Layout**: Changed from single-column rows to responsive grid layout
- **Validation Display**: Moved from inline errors to grouped alert above submit button

### Technical Details

#### Dependencies
- **Production**:
  - next: 15.5.6
  - react: 19.1.0
  - react-dom: 19.1.0
  - typescript: 5.x
  - zustand: 5.0.8
  - date-fns: 4.1.0
  - react-hot-toast: 2.6.0
  - lucide-react: 0.546.0
  - @radix-ui packages (checkbox, label, radio-group, select, slot)
  - class-variance-authority: 0.7.1
  - clsx: 2.1.1
  - tailwind-merge: 3.3.1
  - next-themes: 0.4.6

- **Development**:
  - @tailwindcss/postcss: 4.x
  - tailwindcss: 4.x
  - @types/node: 20.x
  - @types/react: 19.x
  - @types/react-dom: 19.x

#### Project Structure
```
scalper/
├── app/               # Next.js app directory
├── components/        # React components (including ui/)
├── store/            # Zustand state management
├── types/            # TypeScript type definitions
├── utils/            # Utility functions
├── config/           # Configuration files
├── components.json   # shadcn/ui config
└── package.json      # Project dependencies
```

#### Scripts
- `npm run dev`: Start development server with Turbopack
- `npm run build`: Build production application with Turbopack
- `npm start`: Start production server

### Documentation
- **README.md**: Comprehensive project documentation
  - Features overview
  - Installation instructions
  - Usage guide
  - Customization guide
  - API documentation
  - Component details
  - Type definitions
  - Future enhancements

- **config/README.md**: Configuration guide
  - How to add exchanges
  - How to add quantities
  - How to add trailing percentages
  - How to add tickers
  - Troubleshooting tips

- **CHANGELOG.md**: This file, documenting all changes

### Security
- Form validation to prevent invalid data
- Confirmation dialogs for destructive actions
- Type safety throughout the application

### Performance
- Optimized rendering with React 19
- Efficient state management with Zustand
- Turbopack for faster development builds
- Code splitting and lazy loading
- Optimized bundle size

### Accessibility
- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Focus indicators
- High contrast color scheme

---

## Future Versions

### Planned for [0.2.0]
- [ ] Backend API integration
- [ ] WebSocket for real-time price updates
- [ ] User authentication
- [ ] Data persistence

### Planned for [0.3.0]
- [ ] Performance analytics dashboard
- [ ] Charts and graphs
- [ ] Historical data visualization
- [ ] Backtesting functionality

### Planned for [0.4.0]
- [ ] Bot templates
- [ ] Import/Export configurations
- [ ] Advanced risk management
- [ ] Multi-bot strategies

---

**Note**: This is the initial release (v0.1.0) of the Scalper Bot Dashboard. This version focuses on the frontend UI/UX with mock data and no backend integration.
