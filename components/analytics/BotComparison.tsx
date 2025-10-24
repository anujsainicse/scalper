'use client';

import React, { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { useAnalyticsStore } from '@/store/analyticsStore';
import { formatPnL } from '@/utils/formatters';
import { Trophy, Medal, Award } from 'lucide-react';
import { cn } from '@/lib/utils';

export const BotComparison: React.FC = () => {
  const botPerformance = useAnalyticsStore((state) => state.botPerformance);
  const fetchBotPerformance = useAnalyticsStore((state) => state.fetchBotPerformance);
  const isLoading = useAnalyticsStore((state) => state.isLoading);

  useEffect(() => {
    fetchBotPerformance();
  }, [fetchBotPerformance]);

  if (isLoading && botPerformance.length === 0) {
    return <div>Loading...</div>;
  }

  if (botPerformance.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Bot Performance Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            No bot data available
          </div>
        </CardContent>
      </Card>
    );
  }

  const getRankBadge = (rank: number) => {
    if (rank === 1) return <Trophy className="h-4 w-4 text-yellow-500" />;
    if (rank === 2) return <Medal className="h-4 w-4 text-gray-400" />;
    if (rank === 3) return <Award className="h-4 w-4 text-orange-600" />;
    return <span className="text-xs text-muted-foreground">#{rank}</span>;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Bot Performance Ranking</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {botPerformance.map((bot) => (
            <div
              key={bot.botId}
              className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-8">
                  {getRankBadge(bot.rank)}
                </div>
                <div>
                  <div className="font-semibold">{bot.ticker}</div>
                  <div className="text-xs text-muted-foreground">
                    {bot.exchange} • {bot.totalTrades} trades
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <Badge
                  variant={bot.status === 'ACTIVE' ? 'default' : 'secondary'}
                  className="w-20 justify-center"
                >
                  {bot.status}
                </Badge>

                <div className={cn(
                  "text-right font-bold min-w-[100px]",
                  bot.pnl > 0 ? "text-green-500" : "text-red-500"
                )}>
                  {formatPnL(bot.pnl)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
