'use client';

import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { useBotStore } from '@/store/botStore';
import { formatRelativeTime, formatPnL } from '@/utils/formatters';
import { ActiveBot } from '@/types/bot';
import { PriceProximityBar } from './PriceProximityBar';
import {
  Play,
  Square,
  Trash2,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Activity,
  Edit,
} from 'lucide-react';

type BotFilter = 'all' | 'active' | 'stopped';

export const ActiveBots: React.FC = () => {
  const bots = useBotStore((state) => state.bots);
  const toggleBot = useBotStore((state) => state.toggleBot);
  const removeBot = useBotStore((state) => state.removeBot);
  const stopAllBots = useBotStore((state) => state.stopAllBots);
  const setEditingBot = useBotStore((state) => state.setEditingBot);

  const [deletingBot, setDeletingBot] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<BotFilter>('all');

  const activeBots = bots.filter((bot) => bot.status === 'ACTIVE');
  const stoppedBots = bots.filter((bot) => bot.status === 'STOPPED');

  // Filter bots based on active tab
  const filteredBots =
    activeFilter === 'all' ? bots :
    activeFilter === 'active' ? activeBots :
    stoppedBots;

  const handleDeleteBot = async (botId: string) => {
    console.log('[DELETE] handleDeleteBot called with botId:', botId);
    console.log('[DELETE] Current deletingBot state:', deletingBot);

    if (deletingBot === botId) {
      // Second click - actually delete
      console.log('[DELETE] Second click detected - proceeding with deletion');
      try {
        console.log('[DELETE] Calling removeBot API...');
        await removeBot(botId);
        console.log('[DELETE] removeBot completed successfully');
        toast.success('✅ Bot deleted');
        setDeletingBot(null);
        console.log('[DELETE] Deletion complete');
      } catch (error) {
        console.error('[DELETE] Error during deletion:', error);
        console.error('[DELETE] Error details:', error instanceof Error ? error.message : String(error));
        toast.error(`❌ Failed to delete bot: ${error instanceof Error ? error.message : 'Unknown error'}`);
        setDeletingBot(null);
      }
    } else {
      // First click - set confirmation state
      console.log('[DELETE] First click detected - setting confirmation state');
      setDeletingBot(botId);
      toast('🗑️ Click Delete again to confirm', { duration: 3000 });
      setTimeout(() => {
        console.log('[DELETE] Confirmation timeout - resetting state');
        setDeletingBot(null);
      }, 3000);
    }
  };

  const handleStopAll = async () => {
    if (window.confirm('Are you sure you want to stop all bots?')) {
      try {
        await stopAllBots();
        toast.error('🛑 All bots stopped');
      } catch (error) {
        toast.error('❌ Failed to stop bots');
      }
    }
  };

  const handleToggleBot = async (botId: string) => {
    try {
      const bot = bots.find((b) => b.id === botId);
      const willBeActive = bot?.status !== 'ACTIVE';

      await toggleBot(botId);

      const status = willBeActive ? 'started' : 'stopped';
      const icon = willBeActive ? '▶️' : '⏸️';
      toast.success(`${icon} Bot ${status}`);
    } catch (error) {
      toast.error('❌ Failed to toggle bot');
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          {/* Tabs */}
          <div className="flex gap-2 border-b flex-1">
            <button
              onClick={() => setActiveFilter('all')}
              className={`px-4 py-2 text-sm font-medium transition-colors relative ${
                activeFilter === 'all'
                  ? 'text-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              All Bots
              <Badge variant="secondary" className="ml-2">
                {bots.length}
              </Badge>
              {activeFilter === 'all' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
              )}
            </button>

            <button
              onClick={() => setActiveFilter('active')}
              className={`px-4 py-2 text-sm font-medium transition-colors relative ${
                activeFilter === 'active'
                  ? 'text-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Active Bots
              <Badge variant="secondary" className="ml-2 bg-green-600/20 text-green-400">
                {activeBots.length}
              </Badge>
              {activeFilter === 'active' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
              )}
            </button>

            <button
              onClick={() => setActiveFilter('stopped')}
              className={`px-4 py-2 text-sm font-medium transition-colors relative ${
                activeFilter === 'stopped'
                  ? 'text-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Stopped Bots
              <Badge variant="secondary" className="ml-2">
                {stoppedBots.length}
              </Badge>
              {activeFilter === 'stopped' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
              )}
            </button>
          </div>

          {/* Stop All Button */}
          {activeBots.length > 0 && (
            <Button variant="destructive" size="sm" onClick={handleStopAll} className="ml-4">
              <AlertTriangle className="mr-2 h-4 w-4" />
              Stop All
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto">
        {filteredBots.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <Activity className="h-16 w-16 mb-4 opacity-50" />
            {bots.length === 0 ? (
              <>
                <p className="text-lg">No bots configured yet</p>
                <p className="text-sm mt-2">Create a bot to get started</p>
              </>
            ) : (
              <>
                <p className="text-lg">
                  No {activeFilter === 'active' ? 'active' : 'stopped'} bots
                </p>
                <p className="text-sm mt-2">
                  {activeFilter === 'active'
                    ? 'Start a bot to see it here'
                    : 'Stop a bot to see it here'}
                </p>
              </>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
            {filteredBots.map((bot) => (
              <BotCard
                key={bot.id}
                bot={bot}
                onToggle={() => handleToggleBot(bot.id)}
                onDelete={() => handleDeleteBot(bot.id)}
                onEdit={() => setEditingBot(bot.id)}
                isDeleting={deletingBot === bot.id}
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

interface BotCardProps {
  bot: ActiveBot;
  onToggle: () => void;
  onDelete: () => void;
  onEdit: () => void;
  isDeleting: boolean;
}

const BotCard: React.FC<BotCardProps> = ({ bot, onToggle, onDelete, onEdit, isDeleting }) => {
  const [livePrice, setLivePrice] = React.useState<number | null>(null);
  const [priceChange, setPriceChange] = React.useState<number>(0);
  const updateBot = useBotStore((state) => state.updateBot);
  const fetchBots = useBotStore((state) => state.fetchBots);
  const pnlFormatted = formatPnL(bot.pnl);
  const isActive = bot.status === 'ACTIVE';

  const handleToggleInfiniteLoop = async () => {
    const newValue = !bot.infiniteLoop;

    try {
      // Optimistically update UI
      updateBot(bot.id, { infiniteLoop: newValue });

      // Call API to persist change
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/bots/${bot.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ticker: bot.ticker,
          exchange: bot.exchange,
          first_order: bot.firstOrder,
          quantity: bot.quantity,
          buy_price: bot.buyPrice,
          sell_price: bot.sellPrice,
          trailing_percent: bot.trailingPercent || null,
          infinite_loop: newValue,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update bot');
      }

      // Refresh bots from server to ensure sync
      await fetchBots();

      toast.success(`♾️ Infinite loop ${newValue ? 'enabled' : 'disabled'}`);
    } catch (error) {
      // Revert on error
      updateBot(bot.id, { infiniteLoop: bot.infiniteLoop });
      toast.error('❌ Failed to toggle infinite loop');
    }
  };

  // Fetch live price from Redis with polling
  React.useEffect(() => {
    const fetchLivePrice = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/price/ltp?exchange=${encodeURIComponent(bot.exchange)}&ticker=${encodeURIComponent(bot.ticker)}`
        );

        if (response.ok) {
          const data = await response.json();
          if (data.success && data.data?.ltp) {
            const currentPrice = Number(data.data.ltp);
            setLivePrice(currentPrice);

            // Calculate price change
            const change = ((currentPrice - bot.buyPrice) / bot.buyPrice) * 100;
            setPriceChange(change);
          } else {
            // Fallback to midpoint if no data
            const midPrice = (bot.buyPrice + bot.sellPrice) / 2;
            setLivePrice(midPrice);
            setPriceChange(0);
          }
        }
      } catch (error) {
        // Fallback to midpoint on error
        const midPrice = (bot.buyPrice + bot.sellPrice) / 2;
        setLivePrice(midPrice);
        setPriceChange(0);
      }
    };

    // Fetch immediately
    fetchLivePrice();

    // Poll every 2 seconds for live updates
    const interval = setInterval(fetchLivePrice, 2000);

    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, [bot.exchange, bot.ticker, bot.buyPrice, bot.sellPrice]);

  // Calculate position of current price on the gradient bar (0-100%)
  const pricePosition = livePrice
    ? Math.max(0, Math.min(100, ((livePrice - bot.buyPrice) / (bot.sellPrice - bot.buyPrice)) * 100))
    : 50;

  return (
    <div className="bg-card border border-border rounded-2xl p-6 hover:border-muted-foreground/50 transition-all duration-300 shadow-xl">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-3xl font-bold text-foreground mb-1">{bot.ticker}</h3>
          <p className="text-sm text-muted-foreground">{bot.exchange}</p>
        </div>
        <div className="text-right">
          <Badge
            variant="secondary"
            className={`mb-2 px-3 py-1 text-xs font-bold ${
              isActive
                ? 'bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400 border-green-300 dark:border-green-500/30'
                : 'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400 border-amber-300 dark:border-amber-500/30'
            }`}
          >
            {bot.status}
          </Badge>
          <div className={`text-2xl font-bold ${bot.pnl >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
            {pnlFormatted.text}
          </div>
          <p className="text-xs text-muted-foreground mt-1">{bot.totalTrades} trades</p>
        </div>
      </div>

      {/* Price Proximity Indicator */}
      <div className="mb-6">
        <PriceProximityBar
          buyPrice={bot.buyPrice}
          sellPrice={bot.sellPrice}
          currentPrice={livePrice || (bot.buyPrice + bot.sellPrice) / 2}
        />
      </div>

      {/* Buy/Sell Prices */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <p className="text-sm text-muted-foreground mb-1">Buy Price</p>
          <p className="text-3xl font-bold text-green-600 dark:text-green-400">{bot.buyPrice.toFixed(2)}</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-muted-foreground mb-1">Sell Price</p>
          <p className="text-3xl font-bold text-red-600 dark:text-red-400">{bot.sellPrice.toFixed(2)}</p>
        </div>
      </div>

      {/* Quantity & Last Fill */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <p className="text-sm text-muted-foreground mb-1">Quantity</p>
          <p className="text-xl font-semibold text-foreground">{bot.quantity}</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-muted-foreground mb-1">Last Fill</p>
          <p className="text-xl font-semibold text-foreground">
            {bot.lastFillTime ? formatRelativeTime(bot.lastFillTime) : 'Never'}
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <Button
          onClick={onToggle}
          className={`h-14 text-base font-semibold transition-all duration-300 ${
            isActive
              ? 'bg-gray-100 dark:bg-zinc-800 hover:bg-gray-200 dark:hover:bg-zinc-700 text-gray-900 dark:text-white border border-gray-300 dark:border-zinc-700'
              : 'bg-green-600 hover:bg-green-500 text-white shadow-lg shadow-green-500/20'
          }`}
        >
          {isActive ? (
            <>
              <Square className="mr-2 h-5 w-5" />
              Stop
            </>
          ) : (
            <>
              <Play className="mr-2 h-5 w-5" />
              Start
            </>
          )}
        </Button>
        <Button
          onClick={onEdit}
          variant="outline"
          className="h-14 text-base font-semibold bg-gray-100 dark:bg-zinc-900 border-gray-300 dark:border-zinc-700 hover:bg-gray-200 dark:hover:bg-zinc-800 text-gray-700 dark:text-zinc-300"
        >
          <Edit className="mr-2 h-5 w-5" />
          Edit
        </Button>
        <Button
          onClick={onDelete}
          variant="outline"
          className={`h-14 text-base font-semibold transition-all ${
            isDeleting
              ? 'bg-red-600 hover:bg-red-500 text-white border-red-500'
              : 'bg-gray-100 dark:bg-zinc-900 border-gray-300 dark:border-zinc-700 hover:bg-gray-200 dark:hover:bg-zinc-800 text-gray-700 dark:text-zinc-300'
          }`}
        >
          <Trash2 className="mr-1 h-5 w-5" />
          {isDeleting ? 'Yes' : 'Delete'}
        </Button>
      </div>

      {/* Infinite Loop Toggle */}
      <button
        onClick={handleToggleInfiniteLoop}
        className={`w-full rounded-xl p-4 flex items-center justify-between transition-all duration-300 ${
          bot.infiniteLoop
            ? 'bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/30 hover:bg-blue-100 dark:hover:bg-blue-500/20'
            : 'bg-gray-50 dark:bg-zinc-800/50 border border-gray-200 dark:border-zinc-700 hover:bg-gray-100 dark:hover:bg-zinc-800'
        }`}
      >
        <div className="flex items-center gap-2">
          <svg
            className={`w-5 h-5 ${bot.infiniteLoop ? 'text-blue-500 dark:text-blue-400' : 'text-muted-foreground dark:text-zinc-500'}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          <span className={`text-sm font-semibold ${bot.infiniteLoop ? 'text-blue-500 dark:text-blue-400' : 'text-muted-foreground dark:text-zinc-500'}`}>
            Infinite Loop {bot.infiniteLoop ? 'Enabled' : 'Disabled'}
          </span>
        </div>
        <div
          className={`w-11 h-6 rounded-full relative transition-all duration-300 ${
            bot.infiniteLoop ? 'bg-blue-500' : 'bg-gray-300 dark:bg-zinc-700'
          }`}
        >
          <div
            className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all duration-300 ${
              bot.infiniteLoop ? 'right-1' : 'left-1'
            }`}
          />
        </div>
      </button>

      {bot.trailingPercent && (
        <div className="mt-3 text-xs text-muted-foreground text-center">
          Trailing: {bot.trailingPercent}%
        </div>
      )}
    </div>
  );
};
