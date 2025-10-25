'use client';

import { useState } from 'react';
import { BotConfiguration } from '@/components/BotConfiguration';
import { ActiveBots } from '@/components/ActiveBots';
import { ActivityLog } from '@/components/ActivityLog';
import { Orders } from '@/components/Orders';
import { WebSocketMonitor } from '@/components/WebSocketMonitor';
import { AnalyticsDashboard } from '@/components/analytics/AnalyticsDashboard';
import { DataLoader } from '@/components/DataLoader';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { Button } from '@/components/ui/button';
import { FileText, Package, Radio, BarChart3 } from 'lucide-react';

type BottomTab = 'logs' | 'orders' | 'websocket' | 'analytics';

export default function Home() {
  const [activeBottomTab, setActiveBottomTab] = useState<BottomTab>('logs');

  return (
    <ProtectedRoute>
      <DataLoader>
      <div className="p-4 md:p-6">

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

      {/* Bottom Panel - Activity Log, Orders & WebSocket Tabs */}
      <div className="mt-6 h-[500px]">
        <div className="flex gap-3 mb-3">
          <Button
            variant={activeBottomTab === 'logs' ? 'default' : 'outline'}
            size="lg"
            onClick={() => setActiveBottomTab('logs')}
            className={`h-12 px-6 font-semibold transition-all duration-300 ${
              activeBottomTab === 'logs'
                ? 'bg-gradient-to-r from-blue-600 to-blue-500 shadow-lg shadow-blue-500/30'
                : 'bg-muted dark:bg-zinc-900 border-border dark:border-zinc-700 hover:bg-muted/80 dark:hover:bg-zinc-800 text-muted-foreground dark:text-zinc-300'
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
                : 'bg-muted dark:bg-zinc-900 border-border dark:border-zinc-700 hover:bg-muted/80 dark:hover:bg-zinc-800 text-muted-foreground dark:text-zinc-300'
            }`}
          >
            <Package className="mr-2 h-5 w-5" />
            Orders
          </Button>
          <Button
            variant={activeBottomTab === 'websocket' ? 'default' : 'outline'}
            size="lg"
            onClick={() => setActiveBottomTab('websocket')}
            className={`h-12 px-6 font-semibold transition-all duration-300 ${
              activeBottomTab === 'websocket'
                ? 'bg-gradient-to-r from-green-600 to-green-500 shadow-lg shadow-green-500/30'
                : 'bg-muted dark:bg-zinc-900 border-border dark:border-zinc-700 hover:bg-muted/80 dark:hover:bg-zinc-800 text-muted-foreground dark:text-zinc-300'
            }`}
          >
            <Radio className="mr-2 h-5 w-5" />
            WebSocket
          </Button>
          <Button
            variant={activeBottomTab === 'analytics' ? 'default' : 'outline'}
            size="lg"
            onClick={() => setActiveBottomTab('analytics')}
            className={`h-12 px-6 font-semibold transition-all duration-300 ${
              activeBottomTab === 'analytics'
                ? 'bg-gradient-to-r from-orange-600 to-orange-500 shadow-lg shadow-orange-500/30'
                : 'bg-muted dark:bg-zinc-900 border-border dark:border-zinc-700 hover:bg-muted/80 dark:hover:bg-zinc-800 text-muted-foreground dark:text-zinc-300'
            }`}
          >
            <BarChart3 className="mr-2 h-5 w-5" />
            Analytics
          </Button>
        </div>
        <div className="h-[calc(100%-60px)] rounded-xl overflow-hidden border border-border dark:border-zinc-800">
          {activeBottomTab === 'logs' ? (
            <ActivityLog />
          ) : activeBottomTab === 'orders' ? (
            <Orders />
          ) : activeBottomTab === 'websocket' ? (
            <WebSocketMonitor />
          ) : (
            <AnalyticsDashboard />
          )}
        </div>
      </div>
    </div>
    </DataLoader>
    </ProtectedRoute>
  );
}
