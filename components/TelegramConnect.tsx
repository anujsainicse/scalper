'use client';

import * as React from 'react';
import { Radio } from 'lucide-react';
import { useBotStore } from '@/store/botStore';
import { Button } from '@/components/ui/button';
import toast from 'react-hot-toast';

export function TelegramConnect() {
  const telegramConnected = useBotStore((state) => state.telegramConnected);
  const toggleTelegram = useBotStore((state) => state.toggleTelegram);
  const [mounted, setMounted] = React.useState(false);

  // useEffect only runs on the client, so we can safely show the UI
  React.useEffect(() => {
    setMounted(true);
  }, []);

  const handleToggle = () => {
    toggleTelegram();
    toast.success(
      telegramConnected ? 'Telegram disconnected' : 'Telegram connected',
      {
        icon: telegramConnected ? '🔴' : '🟢',
        duration: 2000,
      }
    );
  };

  if (!mounted) {
    return (
      <Button variant="outline" size="default" className="gap-2">
        <Radio className="h-4 w-4" />
        <span className="hidden sm:inline">Telegram</span>
      </Button>
    );
  }

  return (
    <Button
      variant={telegramConnected ? 'default' : 'outline'}
      size="default"
      onClick={handleToggle}
      className={`gap-2 ${
        telegramConnected
          ? 'bg-green-600 hover:bg-green-700 text-white'
          : ''
      }`}
    >
      <Radio
        className={`h-4 w-4 ${
          telegramConnected ? 'animate-pulse' : ''
        }`}
      />
      <span className="hidden sm:inline">
        {telegramConnected ? 'Connected' : 'Connect Telegram'}
      </span>
      <span className="sm:hidden">
        {telegramConnected ? 'On' : 'Off'}
      </span>
      <span className="sr-only">Toggle Telegram connection</span>
    </Button>
  );
}
