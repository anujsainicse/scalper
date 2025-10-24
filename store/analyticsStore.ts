import { create } from 'zustand';
import { api } from '@/lib/api';

export type DateRange = '1D' | '1W' | '1M' | '3M' | 'ALL';

export interface PortfolioMetrics {
  totalPnL: number;
  totalTrades: number;
  activeBots: number;
  totalVolume: number;
  winRate: number;
  avgTradeValue: number;
}

export interface PerformanceMetrics {
  winRate: number;
  profitFactor: number;
  sharpeRatio: number;
  maxDrawdown: number;
  avgTradePnL: number;
  bestTrade: number;
  worstTrade: number;
  totalProfitableTrades: number;
  totalLosingTrades: number;
}

export interface PnLDataPoint {
  timestamp: string;
  pnl: number;
  botId?: string;
  botTicker?: string;
}

export interface TradeRecord {
  id: string;
  botId: string;
  botTicker: string;
  exchange: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  pnl: number;
  executedAt: string;
}

export interface BotPerformance {
  botId: string;
  ticker: string;
  exchange: string;
  totalTrades: number;
  pnl: number;
  winRate: number;
  status: string;
  rank: number;
}

interface AnalyticsStore {
  // State
  dateRange: DateRange;
  selectedBotIds: string[];
  portfolioMetrics: PortfolioMetrics | null;
  performanceMetrics: PerformanceMetrics | null;
  pnlHistory: PnLDataPoint[];
  tradeHistory: TradeRecord[];
  botPerformance: BotPerformance[];
  isLoading: boolean;
  error: string | null;

  // Actions
  setDateRange: (range: DateRange) => void;
  toggleBotSelection: (botId: string) => void;
  clearBotSelection: () => void;
  fetchPortfolioMetrics: () => Promise<void>;
  fetchPerformanceMetrics: () => Promise<void>;
  fetchPnLHistory: () => Promise<void>;
  fetchTradeHistory: () => Promise<void>;
  fetchBotPerformance: () => Promise<void>;
  fetchAllAnalytics: () => Promise<void>;
}

export const useAnalyticsStore = create<AnalyticsStore>((set, get) => ({
  // Initial state
  dateRange: '1W',
  selectedBotIds: [],
  portfolioMetrics: null,
  performanceMetrics: null,
  pnlHistory: [],
  tradeHistory: [],
  botPerformance: [],
  isLoading: false,
  error: null,

  // Set date range
  setDateRange: (range: DateRange) => {
    set({ dateRange: range });
    // Automatically refetch data when date range changes
    get().fetchAllAnalytics();
  },

  // Toggle bot selection for filtering
  toggleBotSelection: (botId: string) => {
    const { selectedBotIds } = get();
    const newSelection = selectedBotIds.includes(botId)
      ? selectedBotIds.filter((id) => id !== botId)
      : [...selectedBotIds, botId];

    set({ selectedBotIds: newSelection });
    get().fetchAllAnalytics();
  },

  // Clear bot selection
  clearBotSelection: () => {
    set({ selectedBotIds: [] });
    get().fetchAllAnalytics();
  },

  // Fetch portfolio metrics
  fetchPortfolioMetrics: async () => {
    try {
      const response = await api.getAnalyticsPortfolio(get().dateRange);
      set({ portfolioMetrics: response });
    } catch (error) {
      console.error('Failed to fetch portfolio metrics:', error);
      set({ error: 'Failed to load portfolio metrics' });
    }
  },

  // Fetch performance metrics
  fetchPerformanceMetrics: async () => {
    try {
      const response = await api.getAnalyticsPerformance(get().dateRange);
      set({ performanceMetrics: response });
    } catch (error) {
      console.error('Failed to fetch performance metrics:', error);
      set({ error: 'Failed to load performance metrics' });
    }
  },

  // Fetch PnL history
  fetchPnLHistory: async () => {
    try {
      const response = await api.getAnalyticsPnLHistory(
        get().dateRange,
        get().selectedBotIds
      );
      set({ pnlHistory: response });
    } catch (error) {
      console.error('Failed to fetch PnL history:', error);
      set({ error: 'Failed to load PnL history' });
    }
  },

  // Fetch trade history
  fetchTradeHistory: async () => {
    try {
      const response = await api.getAnalyticsTradeHistory(
        get().dateRange,
        get().selectedBotIds
      );
      set({ tradeHistory: response });
    } catch (error) {
      console.error('Failed to fetch trade history:', error);
      set({ error: 'Failed to load trade history' });
    }
  },

  // Fetch bot performance comparison
  fetchBotPerformance: async () => {
    try {
      const response = await api.getAnalyticsBotComparison(get().dateRange);
      set({ botPerformance: response });
    } catch (error) {
      console.error('Failed to fetch bot performance:', error);
      set({ error: 'Failed to load bot performance' });
    }
  },

  // Fetch all analytics data
  fetchAllAnalytics: async () => {
    set({ isLoading: true, error: null });
    try {
      await Promise.all([
        get().fetchPortfolioMetrics(),
        get().fetchPerformanceMetrics(),
        get().fetchPnLHistory(),
        get().fetchTradeHistory(),
        get().fetchBotPerformance(),
      ]);
      set({ isLoading: false });
    } catch (error) {
      set({
        error: 'Failed to load analytics data',
        isLoading: false,
      });
    }
  },
}));
