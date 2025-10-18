/**
 * Bot Configuration File
 *
 * Customize dropdown options for the Scalper Bot Dashboard.
 * Add or remove items as needed.
 */

export interface ConfigItem {
  value: string | number;
  label: string;
}

/**
 * Available Exchanges
 * Add new exchanges by adding objects with value and label
 */
export const EXCHANGES: ConfigItem[] = [
  { value: 'CoinDCX F', label: 'CoinDCX F' },
  { value: 'Binance', label: 'Binance' },
  // Add more exchanges here:
  // { value: 'Kraken', label: 'Kraken' },
  // { value: 'Coinbase', label: 'Coinbase' },
];

/**
 * Predefined Quantities
 * Set value to 0 for "Custom" option (allows user to enter any amount)
 */
export const QUANTITIES: ConfigItem[] = [
  { value: 1, label: '1' },
  { value: 2, label: '2' },
  { value: 3, label: '3' },
  { value: 5, label: '5' },
  { value: 10, label: '10' },
  { value: 0, label: 'Custom' },
  // Add more quantities here:
  // { value: 20, label: '20' },
  // { value: 50, label: '50' },
];

/**
 * Trailing Percentage Options
 * Use 'none' as value for no trailing stop
 * Numeric strings represent percentage values
 */
export const TRAILING_PERCENTAGES: ConfigItem[] = [
  { value: 'none', label: 'None' },
  { value: '0.1', label: '0.1%' },
  { value: '0.5', label: '0.5%' },
  { value: '1', label: '1%' },
  // Add more trailing percentages here:
  // { value: '1.5', label: '1.5%' },
  // { value: '2', label: '2%' },
  // { value: '3', label: '3%' },
];

/**
 * Popular Trading Tickers
 * Optional: Pre-populate ticker suggestions (can be used for autocomplete)
 */
export const POPULAR_TICKERS: string[] = [
  'ETH/USDT',
  'BNB/USDT',
  'SOL/USDT',
  'XRP/USDT',
  'ADA/USDT',
  'DOGE/USDT',
  'MATIC/USDT',
  'DOT/USDT',
  'AVAX/USDT',
  // Add more tickers here
];

