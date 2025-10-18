'use client';

import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { useBotStore } from '@/store/botStore';
import { formatRelativeTime, formatPnL } from '@/utils/formatters';
import { ActiveBot } from '@/types/bot';
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

export const ActiveBots: React.FC = () => {
  const bots = useBotStore((state) => state.bots);
  const toggleBot = useBotStore((state) => state.toggleBot);
  const removeBot = useBotStore((state) => state.removeBot);
  const stopAllBots = useBotStore((state) => state.stopAllBots);
  const setEditingBot = useBotStore((state) => state.setEditingBot);

  const [deletingBot, setDeletingBot] = useState<string | null>(null);

  const activeBots = bots.filter((bot) => bot.status === 'ACTIVE');

  const handleDeleteBot = (botId: string) => {
    if (deletingBot === botId) {
      removeBot(botId);
      const toastId = toast.success('Bot deleted', {
        onClick: () => toast.dismiss(toastId),
        style: { cursor: 'pointer' },
      });
      setDeletingBot(null);
    } else {
      setDeletingBot(botId);
      setTimeout(() => setDeletingBot(null), 3000);
    }
  };

  const handleStopAll = () => {
    if (window.confirm('Are you sure you want to stop all bots?')) {
      stopAllBots();
      const toastId = toast.error('All bots stopped', {
        onClick: () => toast.dismiss(toastId),
        style: { cursor: 'pointer' },
      });
    }
  };

  const handleToggleBot = (botId: string) => {
    toggleBot(botId);
    const bot = bots.find((b) => b.id === botId);
    if (bot) {
      const newStatus = bot.status === 'ACTIVE' ? 'stopped' : 'started';
      const toastId = toast.success(`Bot ${newStatus}`, {
        onClick: () => toast.dismiss(toastId),
        style: { cursor: 'pointer' },
      });
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Active Bots ({activeBots.length})</CardTitle>
          {activeBots.length > 0 && (
            <Button variant="destructive" size="sm" onClick={handleStopAll}>
              <AlertTriangle className="mr-2 h-4 w-4" />
              Stop All
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto">
        {bots.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <Activity className="h-16 w-16 mb-4 opacity-50" />
            <p className="text-lg">No bots configured yet</p>
            <p className="text-sm mt-2">Create a bot to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
            {bots.map((bot) => (
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
  const pnlFormatted = formatPnL(bot.pnl);
  const isActive = bot.status === 'ACTIVE';

  return (
    <div className="bg-card border rounded-lg p-4 hover:border-muted-foreground/50 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-lg font-semibold">{bot.ticker}</h3>
            <Badge variant={isActive ? 'default' : 'secondary'} className={isActive ? 'bg-green-600' : ''}>
              {bot.status}
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">{bot.exchange}</p>
        </div>
        <div className="text-right">
          <div className="flex items-center gap-1 text-lg font-bold">
            {bot.pnl >= 0 ? (
              <TrendingUp className="h-4 w-4 text-green-500" />
            ) : (
              <TrendingDown className="h-4 w-4 text-destructive" />
            )}
            <span className={pnlFormatted.color}>{pnlFormatted.text}</span>
          </div>
          <p className="text-xs text-muted-foreground">{bot.totalTrades} trades</p>
        </div>
      </div>

      {/* Details */}
      <div className="grid grid-cols-2 gap-3 mb-3 text-sm">
        <div>
          <p className="text-muted-foreground">Buy Price</p>
          <p className="font-medium">{bot.buyPrice.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Sell Price</p>
          <p className="font-medium">{bot.sellPrice.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Quantity</p>
          <p className="font-medium">{bot.quantity}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Last Fill</p>
          <p className="font-medium">
            {bot.lastFillTime ? formatRelativeTime(bot.lastFillTime) : 'Never'}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <Button
          variant={isActive ? 'secondary' : 'default'}
          size="sm"
          onClick={onToggle}
          className={isActive ? '' : 'bg-green-600 hover:bg-green-700'}
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
          variant="outline"
          size="sm"
          onClick={onEdit}
        >
          <Edit className="mr-2 h-4 w-4" />
          Edit
        </Button>
        <Button
          variant={isDeleting ? 'destructive' : 'outline'}
          size="sm"
          onClick={onDelete}
        >
          <Trash2 className="mr-2 h-4 w-4" />
          {isDeleting ? 'Confirm?' : 'Delete'}
        </Button>
      </div>

      {/* Additional Info */}
      <div className="mt-2 space-y-1">
        {bot.trailingPercent && (
          <div className="text-xs text-muted-foreground">
            Trailing: {bot.trailingPercent}%
          </div>
        )}
        {bot.infiniteLoop && (
          <div className="text-xs text-blue-400">∞ Infinite Loop Enabled</div>
        )}
      </div>
    </div>
  );
};
