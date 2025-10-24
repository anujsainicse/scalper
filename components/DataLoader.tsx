'use client';

import { useEffect } from 'react';
import { useBotStore } from '@/store/botStore';
import { useRealtimeBotUpdates } from '@/hooks/useWebSocket';

export function DataLoader({ children }: { children: React.ReactNode }) {
  const fetchBots = useBotStore((state) => state.fetchBots);
  const fetchLogs = useBotStore((state) => state.fetchLogs);

  // Subscribe to real-time WebSocket updates
  useRealtimeBotUpdates();

  useEffect(() => {
    // Fetch initial data on mount
    fetchBots();
    fetchLogs();

    // No more polling! WebSocket provides real-time updates
    // Only refresh every 60 seconds as a fallback in case of missed WebSocket messages
    const fallbackInterval = setInterval(() => {
      console.log('[DataLoader] Fallback refresh');
      fetchBots();
      fetchLogs();
    }, 60000);

    return () => clearInterval(fallbackInterval);
  }, [fetchBots, fetchLogs]);

  return <>{children}</>;
}
