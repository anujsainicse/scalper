'use client';

import { useEffect } from 'react';
import { useBotStore } from '@/store/botStore';

export function DataLoader({ children }: { children: React.ReactNode }) {
  const fetchBots = useBotStore((state) => state.fetchBots);
  const fetchLogs = useBotStore((state) => state.fetchLogs);

  useEffect(() => {
    // Fetch data on mount
    fetchBots();
    fetchLogs();

    // Set up polling to refresh data every 5 seconds
    const interval = setInterval(() => {
      fetchBots();
      fetchLogs();
    }, 5000);

    return () => clearInterval(interval);
  }, [fetchBots, fetchLogs]);

  return <>{children}</>;
}
