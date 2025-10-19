import { create } from 'zustand';
import { BotConfig, ActiveBot, ActivityLog, BotFormData, LogLevel } from '@/types/bot';
import { generateId } from '@/utils/formatters';
import { api, Bot as ApiBot, ActivityLog as ApiLog } from '@/lib/api';

interface BotStore {
  // State
  bots: ActiveBot[];
  activityLogs: ActivityLog[];
  telegramConnected: boolean;
  editingBotId: string | null;
  isLoading: boolean;
  error: string | null;

  // Bot actions
  fetchBots: () => Promise<void>;
  addBot: (formData: BotFormData) => Promise<void>;
  removeBot: (botId: string) => Promise<void>;
  updateBot: (botId: string, updates: Partial<ActiveBot>) => void;
  updateBotFromForm: (botId: string, formData: BotFormData) => Promise<void>;
  toggleBot: (botId: string) => Promise<void>;
  stopAllBots: () => Promise<void>;
  setEditingBot: (botId: string | null) => void;

  // Log actions
  fetchLogs: () => Promise<void>;
  addLog: (level: LogLevel, message: string, botId?: string) => void;
  clearLogs: () => Promise<void>;

  // Telegram action
  toggleTelegram: () => void;
}

// Helper to convert API bot to ActiveBot
const apiToActiveBot = (apiBot: ApiBot): ActiveBot => ({
  id: apiBot.id,
  ticker: apiBot.ticker,
  exchange: apiBot.exchange as 'CoinDCX F' | 'Binance',
  firstOrder: apiBot.first_order as 'BUY' | 'SELL',
  quantity: apiBot.quantity,
  buyPrice: apiBot.buy_price,
  sellPrice: apiBot.sell_price,
  trailingPercent: apiBot.trailing_percent || undefined,
  infiniteLoop: apiBot.infinite_loop,
  status: apiBot.status,
  createdAt: new Date(apiBot.created_at),
  updatedAt: new Date(apiBot.updated_at),
  pnl: apiBot.pnl,
  totalTrades: apiBot.total_trades,
});

// Helper to convert API log to ActivityLog
const apiToActivityLog = (apiLog: ApiLog): ActivityLog => ({
  id: apiLog.id,
  timestamp: new Date(apiLog.timestamp),
  level: apiLog.level as LogLevel,
  message: apiLog.message,
  botId: apiLog.bot_id || undefined,
});

export const useBotStore = create<BotStore>((set, get) => ({
  // Initial state
  bots: [],
  activityLogs: [],
  telegramConnected: false,
  editingBotId: null,
  isLoading: false,
  error: null,

  // Fetch bots from API
  fetchBots: async () => {
    set({ isLoading: true, error: null });
    try {
      const apiBots = await api.getBots();
      const bots = apiBots.map(apiToActiveBot);
      set({ bots, isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch bots',
        isLoading: false
      });
    }
  },

  // Fetch activity logs from API
  fetchLogs: async () => {
    try {
      const apiLogs = await api.getLogs({ limit: 1000 });
      const activityLogs = apiLogs.map(apiToActivityLog);
      set({ activityLogs });
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    }
  },

  // Bot actions
  addBot: async (formData: BotFormData) => {
    set({ isLoading: true, error: null });
    try {
      await api.createBot({
        ticker: formData.ticker,
        exchange: formData.exchange,
        first_order: formData.firstOrder,
        quantity: formData.customQuantity || formData.quantity,
        buy_price: formData.buyPrice,
        sell_price: formData.sellPrice,
        trailing_percent: formData.trailingPercent || null,
        infinite_loop: formData.infiniteLoop,
      });

      // Fetch updated bots from server to avoid duplicates
      await get().fetchBots();

      // Refresh logs to get the new bot creation log
      await get().fetchLogs();

      set({ isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create bot',
        isLoading: false
      });
      throw error;
    }
  },

  removeBot: async (botId: string) => {
    set({ isLoading: true, error: null });
    try {
      await api.deleteBot(botId);

      set((state) => ({
        bots: state.bots.filter((b) => b.id !== botId),
        isLoading: false,
      }));

      // Refresh logs
      await get().fetchLogs();
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete bot',
        isLoading: false
      });
      throw error;
    }
  },

  updateBot: (botId: string, updates: Partial<ActiveBot>) => {
    set((state) => ({
      bots: state.bots.map((bot) =>
        bot.id === botId
          ? { ...bot, ...updates, updatedAt: new Date() }
          : bot
      ),
    }));
  },

  updateBotFromForm: async (botId: string, formData: BotFormData) => {
    set({ isLoading: true, error: null });
    try {
      await api.updateBot(botId, {
        ticker: formData.ticker,
        exchange: formData.exchange,
        first_order: formData.firstOrder,
        quantity: formData.customQuantity || formData.quantity,
        buy_price: formData.buyPrice,
        sell_price: formData.sellPrice,
        trailing_percent: formData.trailingPercent || null,
        infinite_loop: formData.infiniteLoop,
      });

      // Fetch updated bots from server to avoid duplicates
      await get().fetchBots();

      // Refresh logs
      await get().fetchLogs();

      set({
        editingBotId: null,
        isLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to update bot',
        isLoading: false
      });
      throw error;
    }
  },

  setEditingBot: (botId: string | null) => {
    set(() => ({
      editingBotId: botId,
    }));
  },

  toggleBot: async (botId: string) => {
    set({ isLoading: true, error: null });
    try {
      // Get the bot's current status
      const bot = get().bots.find((b) => b.id === botId);

      if (!bot) {
        throw new Error('Bot not found');
      }

      // Call the appropriate endpoint based on current status
      if (bot.status === 'ACTIVE') {
        // Stop bot and cancel pending orders
        await api.stopBot(botId);
      } else {
        // Start bot and place initial order
        await api.startBot(botId);
      }

      // Fetch updated bots from server to avoid duplicates
      await get().fetchBots();

      // Refresh logs
      await get().fetchLogs();

      set({ isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to toggle bot',
        isLoading: false
      });
      throw error;
    }
  },

  stopAllBots: async () => {
    set({ isLoading: true, error: null });
    try {
      await api.stopAllBots();

      // Fetch updated bots
      await get().fetchBots();

      // Refresh logs
      await get().fetchLogs();

      set({ isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to stop all bots',
        isLoading: false
      });
      throw error;
    }
  },

  // Log actions
  addLog: (level: LogLevel, message: string, botId?: string) => {
    set((state) => ({
      activityLogs: [
        {
          id: generateId(),
          timestamp: new Date(),
          level,
          message,
          botId,
        },
        ...state.activityLogs,
      ].slice(0, 1000), // Keep only last 1000 logs
    }));
  },

  clearLogs: async () => {
    try {
      await api.clearLogs();
      set(() => ({
        activityLogs: [],
      }));
    } catch (error) {
      console.error('Failed to clear logs:', error);
    }
  },

  // Telegram action
  toggleTelegram: () => {
    set((state) => ({
      telegramConnected: !state.telegramConnected,
      activityLogs: [
        {
          id: generateId(),
          timestamp: new Date(),
          level: 'TELEGRAM',
          message: `Telegram ${!state.telegramConnected ? 'connected' : 'disconnected'}`,
        },
        ...state.activityLogs,
      ],
    }));
  },
}));
