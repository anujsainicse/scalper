import { formatDistanceToNow, format } from 'date-fns';

/**
 * Formats a number as currency with specified decimal places
 */
export const formatCurrency = (value: number, decimals: number = 2): string => {
  return value.toFixed(decimals);
};

/**
 * Formats a date to relative time (e.g., "2 mins ago")
 */
export const formatRelativeTime = (date: Date): string => {
  return formatDistanceToNow(date, { addSuffix: true });
};

/**
 * Formats a date to time string (HH:MM:SS)
 */
export const formatTime = (date: Date): string => {
  return format(date, 'HH:mm:ss');
};

/**
 * Formats a date to full timestamp
 */
export const formatTimestamp = (date: Date): string => {
  return format(date, 'yyyy-MM-dd HH:mm:ss');
};

/**
 * Formats PnL with color and sign
 */
export const formatPnL = (value: number): { text: string; color: string } => {
  const sign = value >= 0 ? '+' : '';
  const color = value >= 0 ? 'text-green-500' : 'text-red-500';
  return {
    text: `${sign}${formatCurrency(value)}`,
    color,
  };
};

/**
 * Validates ticker format (e.g., BTC/USDT)
 */
export const validateTicker = (ticker: string): boolean => {
  const tickerRegex = /^[A-Z0-9]+\/[A-Z0-9]+$/;
  return tickerRegex.test(ticker);
};

/**
 * Generates a unique ID
 */
export const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};
