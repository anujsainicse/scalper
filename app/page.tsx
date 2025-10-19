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
      <header className="mb-8 bg-gradient-to-br from-zinc-900 to-zinc-950 border border-zinc-800 rounded-2xl p-6 shadow-2xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold mb-2 bg-gradient-to-r from-green-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
              ⚡ Scalper Bot
            </h1>
            <p className="text-zinc-400 text-lg">
              Configure and manage your cryptocurrency scalping strategies
            </p>
          </div>
          <div className="flex items-center gap-3">
            <TelegramConnect />
            <ThemeToggle />
          </div>
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
      <div className="mt-6 h-[280px]">
        <div className="flex gap-3 mb-3">
          <Button
            variant={activeBottomTab === 'logs' ? 'default' : 'outline'}
            size="lg"
            onClick={() => setActiveBottomTab('logs')}
            className={`h-12 px-6 font-semibold transition-all duration-300 ${
              activeBottomTab === 'logs'
                ? 'bg-gradient-to-r from-blue-600 to-blue-500 shadow-lg shadow-blue-500/30'
                : 'bg-zinc-900 border-zinc-700 hover:bg-zinc-800 text-zinc-300'
            }`}
          >
            <FileText className="mr-2 h-5 w-5" />
            Activity Logs
          </Button>
          <Button
            variant={activeBottomTab === 'orders' ? 'default' : 'outline'}
            size="lg"
            onClick={() => setActiveBottomTab('orders')}
            className={`h-12 px-6 font-semibold transition-all duration-300 ${
              activeBottomTab === 'orders'
                ? 'bg-gradient-to-r from-purple-600 to-purple-500 shadow-lg shadow-purple-500/30'
                : 'bg-zinc-900 border-zinc-700 hover:bg-zinc-800 text-zinc-300'
            }`}
          >
            <Package className="mr-2 h-5 w-5" />
            Orders
          </Button>
        </div>
        <div className="h-[calc(100%-60px)] rounded-xl overflow-hidden border border-zinc-800">
          {activeBottomTab === 'logs' ? <ActivityLog /> : <Orders />}
        </div>
      </div>
    </div>
    </DataLoader>
  );
}
