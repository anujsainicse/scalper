export type Exchange = 'CoinDCX F' | 'Binance';

export type OrderSide = 'BUY' | 'SELL';

export type BotStatus = 'ACTIVE' | 'STOPPED';

export type LogLevel = 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR' | 'TELEGRAM';

export interface BotConfig {
  id: string;
  ticker: string;
  exchange: Exchange;
  firstOrder: OrderSide;
  quantity: number;
  buyPrice: number;
  sellPrice: number;
  trailingPercent?: number;
  infiniteLoop: boolean;
  status: BotStatus;
  createdAt: Date;
  updatedAt: Date;
}

export interface ActiveBot extends BotConfig {
  lastFillTime?: Date;
  pnl: number;
  totalTrades: number;
}

export interface ActivityLog {
  id: string;
  timestamp: Date;
  level: LogLevel;
  message: string;
  botId?: string;
}

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
