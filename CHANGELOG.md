# Changelog

All notable changes to the Scalper Bot Dashboard project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-10-20

### Added

#### Order Cancellation on Bot Deletion
- **Automatic Order Cleanup**: When a bot is deleted, all open orders are automatically cancelled on the exchange
  - Location: `backend/app/api/v1/endpoints/bots.py:273-356`
  - Functionality:
    - Fetches all PENDING orders for the bot being deleted
    - Cancels each order on the exchange using exchange adapter
    - Updates order status to CANCELLED in database
    - Tracks count of successfully cancelled orders
    - Logs activity with cancellation count: "Bot deleted for {ticker} ({N} orders cancelled)"
    - Includes cancellation count in Telegram notification
    - Graceful error handling - continues deletion even if cancellation fails
  - Technical Details:
    - Uses `get_exchange_for_bot()` to get correct exchange adapter
    - Calls `exchange.cancel_order(order_id, symbol)` for each pending order
    - Updates `Order.status = OrderStatus.CANCELLED` in database
    - Uses `db.flush()` to save order updates before bot deletion
  - Activity Log Example: "Bot deleted for ETH/USDT (3 orders cancelled)"
  - Telegram Notification: Shows "Cancelled Orders: 3" when orders are cancelled
  - Error Logging: Logs warnings/errors for failed cancellations but continues

### Fixed

#### Edit Mode Price Overwrite Issue
- **Problem**: When editing a bot, price fields were getting reset every 5 seconds due to polling updates
- **Root Cause**: The `useEffect` in BotConfiguration.tsx depended on both `[editingBotId, bots]` array
  - DataLoader polls backend every 5 seconds
  - Polling updates `bots` array in Zustand store
  - useEffect detects `bots` change and reloads form data
  - User's price edits get overwritten by bot's saved prices
- **Solution**: Changed useEffect dependency from `[editingBotId, bots]` to `[editingBotId]` only
  - Location: `components/BotConfiguration.tsx:55-74`
  - Now form only reloads when user clicks Edit on a different bot
  - Form stays stable during 5-second polling updates
  - Added explanatory comment documenting the fix
  - Added eslint-disable comment for intentional dependency exclusion
- **Result**: Users can now freely edit prices without interference from background polling

## [0.2.0] - 2025-10-20

### Added

#### Reset Button Feature
- **Reset Button in Bot Configuration**: Added reset button in card header (top right corner)
  - Icon: RotateCcw (rotate counter-clockwise) with "reset" label
  - Styling: Red color to indicate reset action
  - Location: Top right of "Bot Configuration" card header
  - Functionality:
    - Resets all form fields to default values
    - Resets ticker to first in POPULAR_TICKERS list (e.g., ETH/USDT)
    - Resets exchange to "CoinDCX F"
    - Resets first order to "BUY"
    - Resets quantity to 1
    - Resets leverage to 3x (default)
    - Resets trailing percent to None
    - Enables infinite loop by default
    - **Fetches fresh LTP data from exchange API**
    - Auto-calculates buy/sell prices based on new LTP (±2%)
    - Updates LTP display with latest market price
    - Clears any active editing mode
    - Clears all validation errors
    - Shows success toast: "✅ Form reset to defaults"

#### Leverage Field Support
- **Complete Leverage Implementation**: Full end-to-end leverage support
  - Frontend: Leverage select dropdown in Bot Configuration
    - Options: 1x, 2x, 3x (default), 5x, 10x, 15x, 20x, 25x, 30x, 35x, 40x, 45x, 50x
    - Located between "Trailing %" and "Enable infinite loop"
  - Backend: Database column with proper integration
    - Column: `leverage INTEGER DEFAULT 3`
    - Stored in `bots` table
    - Nullable with fallback to 3
  - API: Proper leverage passing throughout order flow
    - Create bot endpoint uses `bot.leverage`
    - Start/toggle bot endpoint uses `bot.leverage`
    - Exchange adapters receive correct leverage value
  - Database Migration: Added via SQL script
    - File: `backend/migrate_leverage.sql`
    - Safely adds column if not exists
    - Preserves existing data

### Fixed

#### Critical Leverage Bug
- **Leverage Not Being Applied**: Fixed hardcoded 3x leverage in start_bot function
  - **Root Cause**: Line 342 in `backend/app/api/v1/endpoints/bots.py` had `leverage = 3` hardcoded
  - **Impact**: All orders were placed with 3x leverage regardless of user selection
  - **Solution**: Changed to `leverage = bot.leverage if bot.leverage else 3`
  - **Verification**:
    - Tested with 5x, 10x, 15x, 20x leverage values
    - Confirmed via backend logs showing correct leverage
    - Confirmed via database queries showing correct values
    - Confirmed orders placed with selected leverage
  - **Files Changed**:
    - `backend/app/api/v1/endpoints/bots.py` (lines 342-343)

#### Database Schema Issues
- **Missing Leverage Column**: Added leverage column to existing database
  - Created migration script: `backend/migrate_leverage.sql`
  - Added column safely with DEFAULT 3
  - Cleaned old test data during migration
  - Verified schema with information_schema queries

### Changed

#### LTP Refresh Enhancement
- **Dynamic LTP Updates on Reset**: Reset button now fetches fresh market data
  - Refactored `fetchPriceData` function to accept optional parameters
  - Function signature: `fetchPriceData(ticker?: string, exchange?: Exchange)`
  - Falls back to formData values if parameters not provided
  - Reset function explicitly passes default ticker and exchange
  - Buy/sell prices recalculate automatically based on fresh LTP
  - Loading state shown while fetching ("Loading...")

#### Code Improvements
- **Async Reset Handler**: Made reset function async to support API calls
  - Properly awaits LTP data fetch
  - Sequential execution: reset → fetch → update → notify
  - Better error handling for API failures

### Technical Details

#### Files Modified
1. **components/BotConfiguration.tsx**:
   - Added RotateCcw icon import from lucide-react
   - Created async `handleReset` function (lines 244-273)
   - Refactored `fetchPriceData` to accept parameters (lines 89-125)
   - Updated CardHeader with flexbox layout and reset button (lines 277-290)
   - Total lines changed: ~60 lines

2. **backend/app/api/v1/endpoints/bots.py**:
   - Fixed hardcoded leverage in start_bot function (lines 342-343)
   - Changed: `leverage = 3` → `leverage = bot.leverage if bot.leverage else 3`
   - Added logging for configured leverage
   - Total lines changed: 2 lines

3. **backend/app/models/bot.py**:
   - Already had leverage field (line 39): `leverage = Column(Integer, default=3)`
   - No changes needed

4. **backend/app/schemas/bot.py**:
   - Already had leverage validation (lines 41-42)
   - Validation: `leverage: Optional[int] = Field(3, ge=1, le=50)`
   - No changes needed

5. **Database Migration**:
   - Created: `backend/migrate_leverage.sql`
   - Added leverage column with proper checks
   - Cleaned old test data (6 bots, 15 logs, 2 orders)
   - Verified with SQL queries

#### Testing Performed
- ✅ **Leverage Testing**:
  - Created bots with 5x, 10x, 15x, 20x leverage
  - Verified database stores correct values
  - Confirmed backend logs show correct leverage
  - Tested bot start/toggle with various leverage values
  - All leverage values properly passed to exchange adapters

- ✅ **Reset Button Testing**:
  - Reset clears all form fields correctly
  - LTP fetches fresh data from API
  - Buy/sell prices recalculate accurately
  - Validation errors clear on reset
  - Toast notification displays
  - No console errors

- ✅ **Integration Testing**:
  - Full bot creation flow with custom leverage
  - Edit bot maintains leverage value
  - Toggle bot uses correct leverage
  - Database persists leverage across sessions

#### Backend Logs Verification
```
INFO: Using leverage 5x from bot configuration for ETHUSDT
INFO: Placing buy order for new bot ... with 5x leverage
INFO: Using leverage 10x from bot configuration for BTCUSDT
INFO: Placing buy order for bot ... with 10x leverage
INFO: No existing position for ETHUSDT. Using bot's configured leverage 15x
```

#### Database Verification
```sql
-- Verified leverage column exists
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name='bots' AND column_name='leverage';

-- Result:
-- column_name | data_type | column_default
-- leverage    | integer   | 3

-- Verified test data
SELECT ticker, leverage, created_at FROM bots ORDER BY created_at DESC LIMIT 3;

-- Result:
-- ticker  | leverage | created_at
-- BTCUSDT |       20 | 2025-10-20 18:06:22
-- BTCUSDT |       15 | 2025-10-20 18:06:21
-- BTCUSDT |        5 | 2025-10-20 18:06:20
```

### API Endpoints
No new endpoints added. Existing endpoints now properly handle leverage:
- `POST /api/v1/bots/` - Creates bot with selected leverage
- `POST /api/v1/bots/{bot_id}/start` - Uses bot's configured leverage
- `POST /api/v1/bots/{bot_id}/toggle` - Maintains leverage value
- `GET /api/v1/bots/` - Returns bots with leverage field

### Migration Guide

#### For Existing Installations
1. Stop backend server
2. Run migration script:
   ```bash
   psql -U username -d scalper_bot -f backend/migrate_leverage.sql
   ```
3. Restart backend server
4. Refresh frontend (Next.js hot reload)

#### For New Installations
- No action needed, schema includes leverage column by default

### Performance Impact
- **Minimal**: Reset button adds one API call (~50-100ms)
- **No Impact**: Leverage field adds negligible database overhead
- **Improved**: Refactored fetchPriceData is more reusable

### Security Considerations
- Leverage validation on backend (1-50 range)
- SQL migration uses safe IF NOT EXISTS check
- No new security vulnerabilities introduced

---

## [0.1.1] - 2025-10-18

### Added

#### UI/UX Improvements
- **Three-Tab Filtering System**: Enhanced ActiveBots component with intelligent filtering
  - "All Bots" tab showing complete bot list with count badge
  - "Active Bots" tab showing only running bots with green badge
  - "Stopped Bots" tab showing only stopped bots
  - Visual active indicator (bottom border) for selected tab
  - Real-time count badges that update as bots change status
  - Contextual empty states for each filter type
  - Smooth transitions between tabs

- **Improved Header Layout**: Optimized ActiveBots header structure
  - Removed redundant title heading
  - Moved tabs to primary position in header
  - Tabs on left, "Stop All" button on right
  - Better space utilization and cleaner UI
  - Flex layout for responsive design

- **Default Ticker Selection**: Enhanced user experience in BotConfiguration
  - First ticker (ETH/USDT) now pre-selected by default
  - Eliminates extra click for most common use case
  - Faster bot creation workflow
  - Applied to initial load, form reset, and cancel actions

- **AI Development Guide**: Comprehensive `.claude/CLAUDE.md` documentation
  - Complete project overview and critical guidelines
  - Technology stack documentation (frontend + backend)
  - Detailed project structure with file descriptions
  - Architecture patterns and code examples
  - Component, form, endpoint, and database patterns
  - Common development tasks (adding exchanges, components, endpoints)
  - Code style guidelines and naming conventions
  - Testing guidelines and environment setup
  - Troubleshooting guide with solutions
  - Complete API endpoint reference
  - Deployment checklist
  - Quick command reference
  - 400+ lines of comprehensive AI assistant guidance

### Changed
- **ActiveBots Layout**: Restructured header from title-based to tab-based navigation
- **Bot Form UX**: Changed ticker dropdown from placeholder to pre-selected first option
- **Empty States**: Enhanced with context-aware messaging based on active filter

### Technical Details
- Tab state managed with local `useState<BotFilter>('all')`
- Filtering logic uses array `.filter()` with bot status checks
- Three filtered arrays: `bots`, `activeBots`, `stoppedBots`
- Badge counts update automatically via Zustand store reactivity

---

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
