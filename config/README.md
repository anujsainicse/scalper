# Bot Configuration Guide

This directory contains the configuration file for customizing dropdown options in the Scalper Bot Dashboard.

## Configuration File

**File:** `bot-config.ts`

This file allows you to customize all dropdown options without modifying the main application code.

## How to Customize

### 1. Exchanges

Add or remove exchanges from the dropdown:

```typescript
export const EXCHANGES: ConfigItem[] = [
  { value: 'CoinDCX F', label: 'CoinDCX F' },
  { value: 'Binance', label: 'Binance' },
  { value: 'Kraken', label: 'Kraken' },        // Add new exchange
  { value: 'Coinbase', label: 'Coinbase' },    // Add new exchange
];
```

### 2. Quantities

Add or remove quantity options:

```typescript
export const QUANTITIES: ConfigItem[] = [
  { value: 1, label: '1' },
  { value: 2, label: '2' },
  { value: 3, label: '3' },
  { value: 5, label: '5' },
  { value: 10, label: '10' },
  { value: 20, label: '20' },      // Add new quantity
  { value: 50, label: '50' },      // Add new quantity
  { value: 100, label: '100' },    // Add new quantity
  { value: 0, label: 'Custom' },   // Keep this for custom input
];
```

**Note:** The `{ value: 0, label: 'Custom' }` option allows users to enter any custom quantity. Keep this if you want to allow custom amounts.

### 3. Trailing Percentages

Add or remove trailing percentage options:

```typescript
export const TRAILING_PERCENTAGES: ConfigItem[] = [
  { value: 'none', label: 'None' },
  { value: '0.1', label: '0.1%' },
  { value: '0.5', label: '0.5%' },
  { value: '1', label: '1%' },
  { value: '1.5', label: '1.5%' },    // Add new percentage
  { value: '2', label: '2%' },        // Add new percentage
  { value: '3', label: '3%' },        // Add new percentage
  { value: '5', label: '5%' },        // Add new percentage
];
```

**Note:** The `{ value: 'none', label: 'None' }` option is required for "no trailing stop". Always keep this as the first option.

### 4. Popular Tickers (Optional)

Add commonly used trading pairs for future autocomplete features:

```typescript
export const POPULAR_TICKERS: string[] = [
  'BTC/USDT',
  'ETH/USDT',
  'BNB/USDT',
  'SOL/USDT',
  'XRP/USDT',
  'LINK/USDT',    // Add more tickers
  'UNI/USDT',     // Add more tickers
];
```

## Configuration Format

Each configuration array uses the `ConfigItem` interface:

```typescript
interface ConfigItem {
  value: string | number;  // The actual value stored
  label: string;           // The text displayed to users
}
```

### Examples

**Adding a new exchange:**
```typescript
{ value: 'Bybit', label: 'Bybit Futures' }
```

**Adding a new quantity:**
```typescript
{ value: 25, label: '25 units' }
```

**Adding a new trailing percentage:**
```typescript
{ value: '2.5', label: '2.5% trailing stop' }
```

## Tips

1. **Restart the dev server** after making changes to see them reflected in the UI
2. **Keep values unique** to avoid conflicts
3. **Use descriptive labels** to help users understand options
4. **Order matters** - items appear in the order you define them
5. **Test your changes** by opening dropdowns in the UI

## Example: Adding Multiple Options

```typescript
// Add 3 new exchanges
export const EXCHANGES: ConfigItem[] = [
  { value: 'CoinDCX F', label: 'CoinDCX F' },
  { value: 'Binance', label: 'Binance' },
  { value: 'Bybit', label: 'Bybit' },
  { value: 'OKX', label: 'OKX' },
  { value: 'Gate.io', label: 'Gate.io' },
];

// Add more quantity options
export const QUANTITIES: ConfigItem[] = [
  { value: 1, label: '1' },
  { value: 5, label: '5' },
  { value: 10, label: '10' },
  { value: 25, label: '25' },
  { value: 50, label: '50' },
  { value: 100, label: '100' },
  { value: 0, label: 'Custom' },
];

// Add more trailing percentages
export const TRAILING_PERCENTAGES: ConfigItem[] = [
  { value: 'none', label: 'None' },
  { value: '0.1', label: '0.1%' },
  { value: '0.25', label: '0.25%' },
  { value: '0.5', label: '0.5%' },
  { value: '1', label: '1%' },
  { value: '2', label: '2%' },
  { value: '3', label: '3%' },
  { value: '5', label: '5%' },
];
```

## Troubleshooting

**Changes not appearing?**
- Make sure you saved the `bot-config.ts` file
- Restart the development server (`npm run dev`)
- Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)

**Dropdown showing undefined?**
- Check that each item has both `value` and `label` properties
- Ensure trailing percentages include the `'none'` option
- Verify there are no syntax errors in the TypeScript file

**Getting TypeScript errors?**
- Make sure values are either `string` or `number` types
- Keep the `ConfigItem` interface structure
- Don't use special characters in values without proper escaping
