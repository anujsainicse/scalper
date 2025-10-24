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
import { useKeyboardShortcuts, KeyboardShortcut } from '@/hooks/useKeyboardShortcuts';
import { ShortcutsHelp } from './ShortcutsHelp';
import {
  Play,
  Square,
  Trash2,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Activity,
  Edit,
  Grid3x3,
  List,
  CheckSquare,
  XSquare,
  Search,
  Filter,
  X,
  Keyboard,
} from 'lucide-react';

type BotFilter = 'all' | 'active' | 'stopped';

export const ActiveBots: React.FC = () => {
  const bots = useBotStore((state) => state.bots);
  const toggleBot = useBotStore((state) => state.toggleBot);
  const removeBot = useBotStore((state) => state.removeBot);
  const stopAllBots = useBotStore((state) => state.stopAllBots);
  const setEditingBot = useBotStore((state) => state.setEditingBot);
  const layoutMode = useBotStore((state) => state.layoutMode);
  const setLayoutMode = useBotStore((state) => state.setLayoutMode);
  const selectedBotIds = useBotStore((state) => state.selectedBotIds);
  const toggleBotSelection = useBotStore((state) => state.toggleBotSelection);
  const selectAllBots = useBotStore((state) => state.selectAllBots);
  const clearSelection = useBotStore((state) => state.clearSelection);
  const bulkStartBots = useBotStore((state) => state.bulkStartBots);
  const bulkStopBots = useBotStore((state) => state.bulkStopBots);
  const bulkDeleteBots = useBotStore((state) => state.bulkDeleteBots);

  const [deletingBot, setDeletingBot] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<BotFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [exchangeFilter, setExchangeFilter] = useState<string>('all');
  const [pnlFilter, setPnlFilter] = useState<'all' | 'profit' | 'loss'>('all');
  const [minPnl, setMinPnl] = useState<number | ''>('');
  const [maxPnl, setMaxPnl] = useState<number | ''>('');
  const [showShortcutsHelp, setShowShortcutsHelp] = useState(false);

  const activeBots = bots.filter((bot) => bot.status === 'ACTIVE');
  const stoppedBots = bots.filter((bot) => bot.status === 'STOPPED');

  // Get unique exchanges for filter dropdown
  const uniqueExchanges = Array.from(new Set(bots.map((bot) => bot.exchange)));

  // Filter bots based on active tab, search, and filters
  let filteredBots =
    activeFilter === 'all' ? bots :
    activeFilter === 'active' ? activeBots :
    stoppedBots;

  // Apply search filter
  if (searchQuery.trim()) {
    const query = searchQuery.toLowerCase();
    filteredBots = filteredBots.filter(
      (bot) =>
        bot.ticker.toLowerCase().includes(query) ||
        bot.exchange.toLowerCase().includes(query) ||
        bot.id.toLowerCase().includes(query)
    );
  }

  // Apply exchange filter
  if (exchangeFilter !== 'all') {
    filteredBots = filteredBots.filter((bot) => bot.exchange === exchangeFilter);
  }

  // Apply PnL filter
  if (pnlFilter === 'profit') {
    filteredBots = filteredBots.filter((bot) => bot.pnl > 0);
  } else if (pnlFilter === 'loss') {
    filteredBots = filteredBots.filter((bot) => bot.pnl < 0);
  }

  // Apply PnL range filter
  if (minPnl !== '') {
    filteredBots = filteredBots.filter((bot) => bot.pnl >= minPnl);
  }
  if (maxPnl !== '') {
    filteredBots = filteredBots.filter((bot) => bot.pnl <= maxPnl);
  }

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

  const handleBulkStart = async () => {
    const selectedIds = Array.from(selectedBotIds);
    if (selectedIds.length === 0) {
      toast.error('No bots selected');
      return;
    }

    try {
      await bulkStartBots(selectedIds);
      toast.success(`▶️ Started ${selectedIds.length} bot(s)`);
    } catch (error) {
      toast.error('❌ Failed to start selected bots');
    }
  };

  const handleBulkStop = async () => {
    const selectedIds = Array.from(selectedBotIds);
    if (selectedIds.length === 0) {
      toast.error('No bots selected');
      return;
    }

    try {
      await bulkStopBots(selectedIds);
      toast.success(`⏸️ Stopped ${selectedIds.length} bot(s)`);
    } catch (error) {
      toast.error('❌ Failed to stop selected bots');
    }
  };

  const handleBulkDelete = async () => {
    const selectedIds = Array.from(selectedBotIds);
    if (selectedIds.length === 0) {
      toast.error('No bots selected');
      return;
    }

    if (window.confirm(`Delete ${selectedIds.length} selected bot(s)? This cannot be undone.`)) {
      try {
        await bulkDeleteBots(selectedIds);
        toast.success(`🗑️ Deleted ${selectedIds.length} bot(s)`);
      } catch (error) {
        toast.error('❌ Failed to delete selected bots');
      }
    }
  };

  const handleSelectAll = () => {
    if (selectedBotIds.size === filteredBots.length) {
      clearSelection();
    } else {
      selectAllBots();
    }
  };

  const selectedCount = selectedBotIds.size;
  const allSelected = selectedCount === filteredBots.length && filteredBots.length > 0;

  const clearAllFilters = () => {
    setSearchQuery('');
    setExchangeFilter('all');
    setPnlFilter('all');
    setMinPnl('');
    setMaxPnl('');
  };

  const hasActiveFilters =
    searchQuery.trim() !== '' ||
    exchangeFilter !== 'all' ||
    pnlFilter !== 'all' ||
    minPnl !== '' ||
    maxPnl !== '';

  // Keyboard shortcuts
  const shortcuts: KeyboardShortcut[] = [
    {
      key: '?',
      action: () => setShowShortcutsHelp((prev) => !prev),
      description: 'Toggle keyboard shortcuts help',
    },
    {
      key: 'a',
      ctrl: true,
      action: () => {
        if (filteredBots.length > 0) {
          handleSelectAll();
        }
      },
      description: 'Select/deselect all bots',
    },
    {
      key: 'Escape',
      action: () => {
        if (selectedCount > 0) {
          clearSelection();
        } else if (showShortcutsHelp) {
          setShowShortcutsHelp(false);
        }
      },
      description: 'Clear selection or close dialogs',
    },
    {
      key: 'f',
      ctrl: true,
      action: () => setShowFilters((prev) => !prev),
      description: 'Toggle filters panel',
    },
    {
      key: 's',
      ctrl: true,
      action: () => {
        if (selectedCount > 0) {
          handleBulkStart();
        }
      },
      description: 'Start selected bots',
    },
    {
      key: 'x',
      ctrl: true,
      action: () => {
        if (selectedCount > 0) {
          handleBulkStop();
        }
      },
      description: 'Stop selected bots',
    },
    {
      key: 'Delete',
      action: () => {
        if (selectedCount > 0) {
          handleBulkDelete();
        }
      },
      description: 'Delete selected bots',
    },
    {
      key: 'g',
      action: () => setLayoutMode('grid'),
      description: 'Switch to grid layout',
    },
    {
      key: 'l',
      action: () => setLayoutMode('column'),
      description: 'Switch to list layout',
    },
    {
      key: '1',
      action: () => setActiveFilter('all'),
      description: 'Show all bots',
    },
    {
      key: '2',
      action: () => setActiveFilter('active'),
      description: 'Show active bots only',
    },
    {
      key: '3',
      action: () => setActiveFilter('stopped'),
      description: 'Show stopped bots only',
    },
  ];

  useKeyboardShortcuts(shortcuts, !showShortcutsHelp);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        {/* Search and Filter Bar */}
        <div className="mb-3 space-y-2">
          <div className="flex gap-2">
            {/* Search Input */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search bots by ticker, exchange, or ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 text-sm border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>

            {/* Filter Toggle Button */}
            <Button
              variant={showFilters ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className="h-10 px-4"
            >
              <Filter className="mr-2 h-4 w-4" />
              Filters
              {hasActiveFilters && (
                <Badge variant="secondary" className="ml-2 bg-blue-600 text-white">
                  {[
                    searchQuery.trim() !== '',
                    exchangeFilter !== 'all',
                    pnlFilter !== 'all',
                    minPnl !== '' || maxPnl !== '',
                  ].filter(Boolean).length}
                </Badge>
              )}
            </Button>
          </div>

          {/* Advanced Filters Panel */}
          {showFilters && (
            <div className="p-3 bg-muted/50 border border-border rounded-lg space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {/* Exchange Filter */}
                <div>
                  <label className="text-xs font-medium text-muted-foreground block mb-1">
                    Exchange
                  </label>
                  <select
                    value={exchangeFilter}
                    onChange={(e) => setExchangeFilter(e.target.value)}
                    className="w-full px-3 py-1.5 text-sm border border-border rounded bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="all">All Exchanges</option>
                    {uniqueExchanges.map((exchange) => (
                      <option key={exchange} value={exchange}>
                        {exchange}
                      </option>
                    ))}
                  </select>
                </div>

                {/* PnL Type Filter */}
                <div>
                  <label className="text-xs font-medium text-muted-foreground block mb-1">
                    PnL Type
                  </label>
                  <select
                    value={pnlFilter}
                    onChange={(e) => setPnlFilter(e.target.value as 'all' | 'profit' | 'loss')}
                    className="w-full px-3 py-1.5 text-sm border border-border rounded bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="all">All</option>
                    <option value="profit">Profitable Only</option>
                    <option value="loss">Loss Only</option>
                  </select>
                </div>

                {/* PnL Range */}
                <div>
                  <label className="text-xs font-medium text-muted-foreground block mb-1">
                    PnL Range
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      placeholder="Min"
                      value={minPnl}
                      onChange={(e) => setMinPnl(e.target.value === '' ? '' : Number(e.target.value))}
                      className="w-full px-2 py-1.5 text-sm border border-border rounded bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    <input
                      type="number"
                      placeholder="Max"
                      value={maxPnl}
                      onChange={(e) => setMaxPnl(e.target.value === '' ? '' : Number(e.target.value))}
                      className="w-full px-2 py-1.5 text-sm border border-border rounded bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                </div>
              </div>

              {hasActiveFilters && (
                <div className="flex justify-end">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={clearAllFilters}
                    className="h-7 text-xs"
                  >
                    <X className="mr-1 h-3 w-3" />
                    Clear All Filters
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Bulk Actions Bar (shown when bots are selected) */}
        {selectedCount > 0 && (
          <div className="mb-3 p-3 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/30 rounded-lg flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-sm font-semibold text-blue-700 dark:text-blue-400">
                {selectedCount} bot{selectedCount > 1 ? 's' : ''} selected
              </span>
              <Button
                size="sm"
                variant="outline"
                onClick={clearSelection}
                className="h-7 text-xs border-blue-300 dark:border-blue-500/40 hover:bg-blue-100 dark:hover:bg-blue-500/20"
              >
                <XSquare className="mr-1 h-3 w-3" />
                Clear
              </Button>
            </div>
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={handleBulkStart}
                className="h-8 bg-green-500 hover:bg-green-600 text-white border-0 shadow-sm hover:shadow-md"
              >
                <Play className="mr-1.5 h-3.5 w-3.5" />
                Start All
              </Button>
              <Button
                size="sm"
                onClick={handleBulkStop}
                className="h-8 bg-orange-500 hover:bg-orange-600 text-white border-0 shadow-sm hover:shadow-md"
              >
                <Square className="mr-1.5 h-3.5 w-3.5" />
                Stop All
              </Button>
              <Button
                size="sm"
                onClick={handleBulkDelete}
                className="h-8 bg-red-600 hover:bg-red-700 text-white border-0 shadow-sm hover:shadow-md"
              >
                <Trash2 className="mr-1.5 h-3.5 w-3.5" />
                Delete
              </Button>
            </div>
          </div>
        )}

        <div className="flex items-center justify-between">
          {/* Select All Checkbox + Tabs */}
          <div className="flex gap-2 border-b flex-1">
            {filteredBots.length > 0 && (
              <button
                onClick={handleSelectAll}
                className="px-2 py-2 hover:bg-muted rounded transition-colors"
                title={allSelected ? 'Deselect all' : 'Select all'}
              >
                <CheckSquare className={`h-5 w-5 ${allSelected ? 'text-blue-600 dark:text-blue-400' : 'text-muted-foreground'}`} />
              </button>
            )}
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

          {/* Layout Toggle Buttons */}
          <div className="flex gap-1 ml-auto mr-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setShowShortcutsHelp(true)}
              className="h-8 w-8 p-0"
              title="Keyboard Shortcuts (?)"
            >
              <Keyboard className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant={layoutMode === 'grid' ? 'default' : 'ghost'}
              onClick={() => setLayoutMode('grid')}
              className="h-8 w-8 p-0"
              title="Grid View (G)"
            >
              <Grid3x3 className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant={layoutMode === 'column' ? 'default' : 'ghost'}
              onClick={() => setLayoutMode('column')}
              className="h-8 w-8 p-0"
              title="List View (L)"
            >
              <List className="h-4 w-4" />
            </Button>
          </div>

          {/* Stop All Button */}
          {activeBots.length > 0 && (
            <Button
              size="sm"
              onClick={handleStopAll}
              className="bg-red-600 hover:bg-red-700 text-white border-0 shadow-sm hover:shadow-md"
            >
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
          <div className={layoutMode === 'grid'
            ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3'
            : 'flex flex-col gap-3'
          }>
            {filteredBots.map((bot) => (
              <BotCard
                key={bot.id}
                bot={bot}
                onToggle={() => handleToggleBot(bot.id)}
                onDelete={() => handleDeleteBot(bot.id)}
                onEdit={() => setEditingBot(bot.id)}
                isDeleting={deletingBot === bot.id}
                layoutMode={layoutMode}
                isSelected={selectedBotIds.has(bot.id)}
                onSelect={() => toggleBotSelection(bot.id)}
              />
            ))}
          </div>
        )}
      </CardContent>

      {/* Keyboard Shortcuts Help Modal */}
      {showShortcutsHelp && (
        <ShortcutsHelp
          shortcuts={shortcuts}
          onClose={() => setShowShortcutsHelp(false)}
        />
      )}
    </Card>
  );
};

interface BotCardProps {
  bot: ActiveBot;
  onToggle: () => void;
  onDelete: () => void;
  onEdit: () => void;
  isDeleting: boolean;
  layoutMode: 'grid' | 'column';
  isSelected: boolean;
  onSelect: () => void;
}

const BotCard: React.FC<BotCardProps> = ({ bot, onToggle, onDelete, onEdit, isDeleting, layoutMode, isSelected, onSelect }) => {
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

  // Column layout (horizontal)
  if (layoutMode === 'column') {
    return (
      <div className={`bg-card border rounded-xl p-4 hover:border-muted-foreground/50 transition-all duration-300 shadow-lg ${
        isSelected ? 'border-blue-500 dark:border-blue-400 bg-blue-50/50 dark:bg-blue-500/5' : 'border-border'
      }`}>
        <div className="flex items-center gap-4">
          {/* Checkbox */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onSelect();
            }}
            className="shrink-0"
            title={isSelected ? 'Deselect' : 'Select'}
          >
            <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
              isSelected
                ? 'bg-blue-600 border-blue-600 dark:bg-blue-500 dark:border-blue-500'
                : 'border-gray-300 dark:border-zinc-600 hover:border-blue-400 dark:hover:border-blue-500'
            }`}>
              {isSelected && (
                <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </div>
          </button>

          {/* Status Badge */}
          <Badge
            variant="secondary"
            className={`px-2 py-1 text-xs font-bold shrink-0 ${
              isActive
                ? 'bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400 border-green-300 dark:border-green-500/30'
                : 'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400 border-amber-300 dark:border-amber-500/30'
            }`}
          >
            {bot.status}
          </Badge>

          {/* Bot Info - Main Row */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-1.5">
              <h3 className="text-lg font-bold text-foreground">{bot.ticker}</h3>
              <span className="text-sm text-muted-foreground">•</span>
              <span className="text-sm text-muted-foreground">{bot.exchange}</span>
              <span className="text-sm text-muted-foreground">•</span>
              <span className="text-sm text-muted-foreground">Qty: <span className="font-semibold text-foreground">{bot.quantity}</span></span>
              <span className="text-sm text-muted-foreground">•</span>
              <span className="text-sm text-green-600 dark:text-green-400 font-semibold">Buy@{bot.buyPrice.toFixed(2)}</span>
              <span className="text-sm text-red-600 dark:text-red-400 font-semibold">Sell@{bot.sellPrice.toFixed(2)}</span>
            </div>

            {/* Second Row - Details */}
            <div className="flex items-center gap-3 text-sm">
              <span className={`font-semibold ${bot.pnl >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {pnlFormatted.text}
              </span>
              <span className="text-muted-foreground">•</span>
              <span className="text-muted-foreground">Trades: <span className="font-medium text-foreground">{bot.totalTrades}</span></span>
              <span className="text-muted-foreground">•</span>
              {bot.lastFillTime && bot.lastFillSide && bot.lastFillPrice ? (
                <span className={bot.lastFillSide === 'BUY' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                  Last: {bot.lastFillSide}@{bot.lastFillPrice.toFixed(2)} ({formatRelativeTime(bot.lastFillTime)})
                </span>
              ) : (
                <span className="text-muted-foreground">Last: <span className="text-foreground">Never</span></span>
              )}
              {bot.infiniteLoop && (
                <>
                  <span className="text-muted-foreground">•</span>
                  <span className="text-blue-500 dark:text-blue-400 text-xs font-medium">♾️ Loop</span>
                </>
              )}
              {livePrice && (
                <>
                  <span className="text-muted-foreground">•</span>
                  <span className={`text-sm font-semibold ${priceChange >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                    LTP: {livePrice.toFixed(2)}
                  </span>
                </>
              )}
              {bot.trailingPercent && (
                <>
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground text-xs">Trailing: <span className="text-foreground font-medium">{bot.trailingPercent}%</span></span>
                </>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 shrink-0">
            <Button
              onClick={onToggle}
              size="sm"
              className={`h-9 px-4 font-semibold transition-all shadow-sm hover:shadow-md ${
                isActive
                  ? 'bg-orange-500 hover:bg-orange-600 text-white border-0'
                  : 'bg-green-500 hover:bg-green-600 text-white border-0'
              }`}
            >
              {isActive ? <Square className="mr-1.5 h-4 w-4" /> : <Play className="mr-1.5 h-4 w-4" />}
              {isActive ? 'Stop' : 'Start'}
            </Button>
            <Button
              onClick={onEdit}
              size="sm"
              className="h-9 px-4 font-semibold bg-blue-500 hover:bg-blue-600 text-white border-0 shadow-sm hover:shadow-md transition-all"
            >
              <Edit className="mr-1.5 h-4 w-4" />
              Edit
            </Button>
            <Button
              onClick={onDelete}
              size="sm"
              variant="outline"
              className={`h-9 px-4 font-semibold transition-all shadow-sm hover:shadow-md ${
                isDeleting
                  ? 'bg-red-600 hover:bg-red-700 text-white border-red-600'
                  : 'border-2 border-red-500 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/50'
              }`}
            >
              <Trash2 className="mr-1.5 h-4 w-4" />
              {isDeleting ? 'Confirm' : 'Delete'}
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Grid layout (vertical - original)
  return (
    <div className={`bg-card border rounded-2xl p-6 hover:border-muted-foreground/50 transition-all duration-300 shadow-xl ${
      isSelected ? 'border-blue-500 dark:border-blue-400 bg-blue-50/50 dark:bg-blue-500/5' : 'border-border'
    }`}>
      {/* Checkbox - Top Right Corner */}
      <div className="flex items-start justify-between mb-4">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onSelect();
          }}
          className="shrink-0"
          title={isSelected ? 'Deselect' : 'Select'}
        >
          <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
            isSelected
              ? 'bg-blue-600 border-blue-600 dark:bg-blue-500 dark:border-blue-500'
              : 'border-gray-300 dark:border-zinc-600 hover:border-blue-400 dark:hover:border-blue-500'
          }`}>
            {isSelected && (
              <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
        </button>
      </div>

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
          <p className="text-xl font-semibold">
            {bot.lastFillTime && bot.lastFillSide && bot.lastFillPrice ? (
              <span className={bot.lastFillSide === 'BUY' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                {bot.lastFillSide}@{bot.lastFillPrice.toFixed(2)}
              </span>
            ) : (
              <span className="text-foreground">Never</span>
            )}
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <Button
          onClick={onToggle}
          className={`h-12 text-base font-semibold transition-all shadow-md hover:shadow-lg ${
            isActive
              ? 'bg-orange-500 hover:bg-orange-600 text-white border-0'
              : 'bg-green-500 hover:bg-green-600 text-white border-0 shadow-green-500/20'
          }`}
        >
          {isActive ? (
            <>
              <Square className="mr-2 h-4 w-4" />
              Stop
            </>
          ) : (
            <>
              <Play className="mr-2 h-4 w-4" />
              Start
            </>
          )}
        </Button>
        <Button
          onClick={onEdit}
          className="h-12 text-base font-semibold bg-blue-500 hover:bg-blue-600 text-white border-0 shadow-md hover:shadow-lg transition-all"
        >
          <Edit className="mr-2 h-4 w-4" />
          Edit
        </Button>
        <Button
          onClick={onDelete}
          variant="outline"
          className={`h-12 text-base font-semibold transition-all shadow-md hover:shadow-lg ${
            isDeleting
              ? 'bg-red-600 hover:bg-red-700 text-white border-red-600'
              : 'border-2 border-red-500 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/50'
          }`}
        >
          <Trash2 className="mr-2 h-4 w-4" />
          {isDeleting ? 'Confirm' : 'Delete'}
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
