'use client';

import React, { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { useAnalyticsStore } from '@/store/analyticsStore';
import { formatPnL } from '@/utils/formatters';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart3,
  Target,
  Percent,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export const PortfolioOverview: React.FC = () => {
  const portfolioMetrics = useAnalyticsStore((state) => state.portfolioMetrics);
  const fetchPortfolioMetrics = useAnalyticsStore((state) => state.fetchPortfolioMetrics);
  const isLoading = useAnalyticsStore((state) => state.isLoading);

  useEffect(() => {
    fetchPortfolioMetrics();
  }, [fetchPortfolioMetrics]);

  if (isLoading && !portfolioMetrics) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="pb-2">
              <div className="h-4 bg-muted rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-muted rounded w-3/4"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const metrics = portfolioMetrics || {
    totalPnL: 0,
    totalTrades: 0,
    activeBots: 0,
    totalVolume: 0,
    winRate: 0,
    avgTradeValue: 0,
  };

  const isProfitable = metrics.totalPnL > 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {/* Total PnL Card */}
      <Card className="border-2">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total PnL
            </CardTitle>
            {isProfitable ? (
              <TrendingUp className="h-4 w-4 text-green-500" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500" />
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div
            className={cn(
              'text-3xl font-bold',
              isProfitable ? 'text-green-500' : 'text-red-500'
            )}
          >
            {formatPnL(metrics.totalPnL).text}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Combined across all bots
          </p>
        </CardContent>
      </Card>

      {/* Total Trades Card */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Trades
            </CardTitle>
            <Activity className="h-4 w-4 text-blue-500" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">{metrics.totalTrades}</div>
          <p className="text-xs text-muted-foreground mt-1">
            Executed trades
          </p>
        </CardContent>
      </Card>

      {/* Active Bots Card */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Active Bots
            </CardTitle>
            <BarChart3 className="h-4 w-4 text-purple-500" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">{metrics.activeBots}</div>
          <p className="text-xs text-muted-foreground mt-1">
            Currently trading
          </p>
        </CardContent>
      </Card>

      {/* Total Volume Card */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Volume
            </CardTitle>
            <Target className="h-4 w-4 text-orange-500" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">
            ${metrics.totalVolume.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Trading volume
          </p>
        </CardContent>
      </Card>

      {/* Win Rate Card */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Win Rate
            </CardTitle>
            <Percent className="h-4 w-4 text-green-500" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">
            {metrics.winRate.toFixed(1)}%
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Success rate
          </p>
        </CardContent>
      </Card>

      {/* Avg Trade Value Card */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Avg Trade Value
            </CardTitle>
            <Activity className="h-4 w-4 text-cyan-500" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">
            ${metrics.avgTradeValue.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Per trade
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
