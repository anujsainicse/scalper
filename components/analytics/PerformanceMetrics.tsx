'use client';

import React, { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { useAnalyticsStore } from '@/store/analyticsStore';
import { TrendingUp, TrendingDown, Target, Award } from 'lucide-react';
import { cn } from '@/lib/utils';

export const PerformanceMetrics: React.FC = () => {
  const performanceMetrics = useAnalyticsStore((state) => state.performanceMetrics);
  const fetchPerformanceMetrics = useAnalyticsStore((state) => state.fetchPerformanceMetrics);
  const isLoading = useAnalyticsStore((state) => state.isLoading);

  useEffect(() => {
    fetchPerformanceMetrics();
  }, [fetchPerformanceMetrics]);

  if (isLoading && !performanceMetrics) {
    return <div>Loading...</div>;
  }

  const metrics = performanceMetrics || {
    winRate: 0,
    profitFactor: 0,
    sharpeRatio: 0,
    maxDrawdown: 0,
    avgTradePnL: 0,
    bestTrade: 0,
    worstTrade: 0,
    totalProfitableTrades: 0,
    totalLosingTrades: 0,
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {/* Win Rate */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Win Rate
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-green-500">
            {metrics.winRate.toFixed(1)}%
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {metrics.totalProfitableTrades} wins / {metrics.totalLosingTrades} losses
          </p>
        </CardContent>
      </Card>

      {/* Profit Factor */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Profit Factor
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">
            {metrics.profitFactor.toFixed(2)}x
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Gross profit / Gross loss
          </p>
        </CardContent>
      </Card>

      {/* Sharpe Ratio */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Sharpe Ratio
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">
            {metrics.sharpeRatio.toFixed(2)}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Risk-adjusted returns
          </p>
        </CardContent>
      </Card>

      {/* Max Drawdown */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Max Drawdown
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-red-500">
            ${metrics.maxDrawdown.toFixed(2)}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Largest peak-to-trough decline
          </p>
        </CardContent>
      </Card>

      {/* Average Trade PnL */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Avg Trade PnL
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className={cn(
            "text-3xl font-bold",
            metrics.avgTradePnL > 0 ? "text-green-500" : "text-red-500"
          )}>
            ${metrics.avgTradePnL.toFixed(2)}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Average profit per trade
          </p>
        </CardContent>
      </Card>

      {/* Best/Worst Trade */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Best / Worst Trade
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div>
              <span className="text-sm text-muted-foreground">Best: </span>
              <span className="text-lg font-bold text-green-500">
                ${metrics.bestTrade.toFixed(2)}
              </span>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Worst: </span>
              <span className="text-lg font-bold text-red-500">
                ${metrics.worstTrade.toFixed(2)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
