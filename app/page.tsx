'use client';

import { useState } from 'react';
import { BotConfiguration } from '@/components/BotConfiguration';
import { ActiveBots } from '@/components/ActiveBots';
import { ActivityLog } from '@/components/ActivityLog';
import { Orders } from '@/components/Orders';
import { ThemeToggle } from '@/components/ThemeToggle';
import { TelegramConnect } from '@/components/TelegramConnect';
import { DataLoader } from '@/components/DataLoader';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, Package } from 'lucide-react';

type BottomTab = 'logs' | 'orders';

export default function Home() {
  const [activeBottomTab, setActiveBottomTab] = useState<BottomTab>('logs');

  return (
    <DataLoader>
      <div className="min-h-screen p-4 md:p-6">
      {/* Header */}
      <header className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            ⚡ Scalper
          </h1>
          <p className="text-muted-foreground">
            Configure and manage your cryptocurrency scalping bots
          </p>
        </div>
        <div className="flex items-center gap-2">
          <TelegramConnect />
          <ThemeToggle />
        </div>
      </header>

      {/* Main Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-[calc(100vh-180px)]">
        {/* Left Panel - Bot Configuration */}
        <div className="lg:col-span-4 overflow-y-auto">
          <BotConfiguration />
        </div>

        {/* Right Panel - Active Bots */}
        <div className="lg:col-span-8 overflow-y-auto">
          <ActiveBots />
        </div>
      </div>

      {/* Bottom Panel - Activity Log & Orders Tabs */}
      <div className="mt-4 h-[280px]">
        <div className="flex gap-2 mb-2">
          <Button
            variant={activeBottomTab === 'logs' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveBottomTab('logs')}
            className="h-9"
          >
            <FileText className="mr-2 h-4 w-4" />
            Activity Logs
          </Button>
          <Button
            variant={activeBottomTab === 'orders' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveBottomTab('orders')}
            className="h-9"
          >
            <Package className="mr-2 h-4 w-4" />
            Orders
          </Button>
        </div>
        <div className="h-[calc(100%-48px)]">
          {activeBottomTab === 'logs' ? <ActivityLog /> : <Orders />}
        </div>
      </div>
    </div>
    </DataLoader>
  );
}
