'use client';

import { useEffect } from 'react';
import { useWebSocket as useWebSocketContext, WebSocketMessage, WebSocketMessageType } from '@/contexts/WebSocketContext';
import { useBotStore } from '@/store/botStore';
import { ActiveBot, ActivityLog } from '@/types/bot';

/**
 * Hook to listen for bot updates via WebSocket
 */
export const useBotUpdates = () => {
  const { subscribe } = useWebSocketContext();
  const updateBot = useBotStore((state) => state.updateBot);
  const fetchBots = useBotStore((state) => state.fetchBots);

  useEffect(() => {
    const unsubscribe = subscribe(['bot_update', 'bot_created', 'bot_deleted'], (message: WebSocketMessage) => {
      console.log('[useBotUpdates] Received:', message.type, message.data);

      if (message.type === 'bot_update') {
        // Update specific bot in store
        const botData = message.data as Partial<ActiveBot>;
        if (botData.id) {
          updateBot(botData.id, botData);
        }
      } else if (message.type === 'bot_created' || message.type === 'bot_deleted') {
        // Refetch all bots for create/delete operations
        fetchBots();
      }
    });

    return unsubscribe;
  }, [subscribe, updateBot, fetchBots]);
};

/**
 * Hook to listen for order updates via WebSocket
 */
export const useOrderUpdates = () => {
  const { subscribe } = useWebSocketContext();
  const fetchBot = useBotStore((state) => state.fetchBot);

  useEffect(() => {
    const unsubscribe = subscribe(['order_update', 'order_filled'], (message: WebSocketMessage) => {
      console.log('[useOrderUpdates] Received:', message.type, message.data);

      const orderData = message.data;
      if (orderData.bot_id) {
        // Refresh the specific bot to get updated order info
        fetchBot(orderData.bot_id);
      }
    });

    return unsubscribe;
  }, [subscribe, fetchBot]);
};

/**
 * Hook to listen for activity log updates via WebSocket
 */
export const useActivityLogUpdates = () => {
  const { subscribe } = useWebSocketContext();
  const addLog = useBotStore((state) => state.addLog);

  useEffect(() => {
    const unsubscribe = subscribe('log_created', (message: WebSocketMessage) => {
      console.log('[useActivityLogUpdates] Received:', message.type, message.data);

      const logData = message.data as ActivityLog;
      addLog(logData.level, logData.message, logData.botId);
    });

    return unsubscribe;
  }, [subscribe, addLog]);
};

/**
 * Hook to listen for price updates via WebSocket
 * Returns a map of ticker -> latest price
 */
export const usePriceUpdates = (tickers: string[]) => {
  const { subscribe } = useWebSocketContext();

  useEffect(() => {
    if (tickers.length === 0) return;

    const unsubscribe = subscribe('price_update', (message: WebSocketMessage) => {
      const priceData = message.data;
      console.log('[usePriceUpdates] Price update:', priceData.ticker, priceData.price);

      // Price updates are handled by individual bot cards
      // This hook just ensures subscription is active
    });

    return unsubscribe;
  }, [subscribe, tickers]);
};

/**
 * Hook to listen for PnL updates via WebSocket
 */
export const usePnLUpdates = () => {
  const { subscribe } = useWebSocketContext();
  const updateBot = useBotStore((state) => state.updateBot);

  useEffect(() => {
    const unsubscribe = subscribe('pnl_update', (message: WebSocketMessage) => {
      console.log('[usePnLUpdates] Received:', message.type, message.data);

      const pnlData = message.data;
      if (pnlData.bot_id && pnlData.pnl !== undefined) {
        updateBot(pnlData.bot_id, { pnl: pnlData.pnl });
      }
    });

    return unsubscribe;
  }, [subscribe, updateBot]);
};

/**
 * Combined hook to subscribe to all bot-related updates
 */
export const useRealtimeBotUpdates = () => {
  useBotUpdates();
  useOrderUpdates();
  useActivityLogUpdates();
  usePnLUpdates();
};
