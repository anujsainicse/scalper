import { create } from 'zustand';
import { BotConfig, ActiveBot, ActivityLog, BotFormData, LogLevel } from '@/types/bot';
import { generateId } from '@/utils/formatters';

interface BotStore {
  // State
  bots: ActiveBot[];
  activityLogs: ActivityLog[];
  telegramConnected: boolean;
  editingBotId: string | null;

  // Bot actions
  addBot: (formData: BotFormData) => void;
  removeBot: (botId: string) => void;
  updateBot: (botId: string, updates: Partial<ActiveBot>) => void;
  updateBotFromForm: (botId: string, formData: BotFormData) => void;
  toggleBot: (botId: string) => void;
  stopAllBots: () => void;
  setEditingBot: (botId: string | null) => void;

  // Log actions
  addLog: (level: LogLevel, message: string, botId?: string) => void;
  clearLogs: () => void;

  // Telegram action
  toggleTelegram: () => void;
}

export const useBotStore = create<BotStore>((set) => ({
  // Initial state
  bots: [],
  activityLogs: [],
  telegramConnected: false,
  editingBotId: null,

  // Bot actions
  addBot: (formData: BotFormData) => {
    const newBot: ActiveBot = {
      id: generateId(),
      ticker: formData.ticker,
      exchange: formData.exchange,
      firstOrder: formData.firstOrder,
      quantity: formData.customQuantity || formData.quantity,
      buyPrice: formData.buyPrice,
      sellPrice: formData.sellPrice,
      trailingPercent: formData.trailingPercent,
      infiniteLoop: formData.infiniteLoop,
      status: 'ACTIVE',
      createdAt: new Date(),
      updatedAt: new Date(),
      pnl: 0,
      totalTrades: 0,
    };

    set((state) => ({
      bots: [...state.bots, newBot],
      activityLogs: [
        {
          id: generateId(),
          timestamp: new Date(),
          level: 'SUCCESS',
          message: `Bot started for ${newBot.ticker} on ${newBot.exchange}`,
          botId: newBot.id,
        },
        ...state.activityLogs,
      ],
    }));
  },

  removeBot: (botId: string) => {
    set((state) => {
      const bot = state.bots.find((b) => b.id === botId);
      return {
        bots: state.bots.filter((b) => b.id !== botId),
        activityLogs: [
          {
            id: generateId(),
            timestamp: new Date(),
            level: 'WARNING',
            message: `Bot deleted for ${bot?.ticker}`,
            botId,
          },
          ...state.activityLogs,
        ],
      };
    });
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

  updateBotFromForm: (botId: string, formData: BotFormData) => {
    set((state) => {
      const bot = state.bots.find((b) => b.id === botId);
      return {
        bots: state.bots.map((b) =>
          b.id === botId
            ? {
                ...b,
                ticker: formData.ticker,
                exchange: formData.exchange,
                firstOrder: formData.firstOrder,
                quantity: formData.customQuantity || formData.quantity,
                buyPrice: formData.buyPrice,
                sellPrice: formData.sellPrice,
                trailingPercent: formData.trailingPercent,
                infiniteLoop: formData.infiniteLoop,
                updatedAt: new Date(),
              }
            : b
        ),
        editingBotId: null,
        activityLogs: [
          {
            id: generateId(),
            timestamp: new Date(),
            level: 'INFO',
            message: `Bot updated for ${formData.ticker} on ${formData.exchange}`,
            botId,
          },
          ...state.activityLogs,
        ],
      };
    });
  },

  setEditingBot: (botId: string | null) => {
    set(() => ({
      editingBotId: botId,
    }));
  },

  toggleBot: (botId: string) => {
    set((state) => {
      const bot = state.bots.find((b) => b.id === botId);
      const newStatus = bot?.status === 'ACTIVE' ? 'STOPPED' : 'ACTIVE';
      const level = newStatus === 'ACTIVE' ? 'SUCCESS' : 'WARNING';
      const message = `Bot ${newStatus.toLowerCase()} for ${bot?.ticker}`;

      return {
        bots: state.bots.map((b) =>
          b.id === botId
            ? { ...b, status: newStatus, updatedAt: new Date() }
            : b
        ),
        activityLogs: [
          {
            id: generateId(),
            timestamp: new Date(),
            level,
            message,
            botId,
          },
          ...state.activityLogs,
        ],
      };
    });
  },

  stopAllBots: () => {
    set((state) => ({
      bots: state.bots.map((bot) => ({
        ...bot,
        status: 'STOPPED' as const,
        updatedAt: new Date(),
      })),
      activityLogs: [
        {
          id: generateId(),
          timestamp: new Date(),
          level: 'ERROR',
          message: 'Emergency stop - All bots stopped',
        },
        ...state.activityLogs,
      ],
    }));
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

  clearLogs: () => {
    set(() => ({
      activityLogs: [],
    }));
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
