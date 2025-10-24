'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { PortfolioOverview } from './PortfolioOverview';
import { PnLChart } from './PnLChart';
import { PerformanceMetrics } from './PerformanceMetrics';
import { BotComparison } from './BotComparison';
import { useAnalyticsStore, DateRange } from '@/store/analyticsStore';
import { BarChart3, TrendingUp, List, Award } from 'lucide-react';

type AnalyticsTab = 'overview' | 'performance' | 'pnl-chart' | 'bot-comparison';

export const AnalyticsDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<AnalyticsTab>('overview');
  const dateRange = useAnalyticsStore((state) => state.dateRange);
  const setDateRange = useAnalyticsStore((state) => state.setDateRange);

  const tabs: {value: AnalyticsTab; label: string; icon: React.ReactNode}[] = [
    { value: 'overview', label: 'Overview', icon: <BarChart3 className="h-4 w-4" /> },
    { value: 'pnl-chart', label: 'PnL Chart', icon: <TrendingUp className="h-4 w-4" /> },
    { value: 'performance', label: 'Performance', icon: <Award className="h-4 w-4" /> },
    { value: 'bot-comparison', label: 'Bot Comparison', icon: <List className="h-4 w-4" /> },
  ];

  const dateRanges: {value: DateRange; label: string}[] = [
    { value: '1D', label: '1D' },
    { value: '1W', label: '1W' },
    { value: '1M', label: '1M' },
    { value: '3M', label: '3M' },
    { value: 'ALL', label: 'All' },
  ];

  return (
    <div className="space-y-4">
      {/* Header with date range selector */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Analytics Dashboard</CardTitle>
            <div className="flex items-center gap-2">
              {dateRanges.map((range) => (
                <Button
                  key={range.value}
                  variant={dateRange === range.value ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setDateRange(range.value)}
                >
                  {range.label}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Tab navigation */}
      <div className="flex gap-2 border-b">
        {tabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setActiveTab(tab.value)}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
              activeTab === tab.value
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="mt-4">
        {activeTab === 'overview' && <PortfolioOverview />}
        {activeTab === 'pnl-chart' && <PnLChart />}
        {activeTab === 'performance' && <PerformanceMetrics />}
        {activeTab === 'bot-comparison' && <BotComparison />}
      </div>
    </div>
  );
};
