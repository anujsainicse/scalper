'use client';

import React, { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { useAnalyticsStore } from '@/store/analyticsStore';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

export const PnLChart: React.FC = () => {
  const pnlHistory = useAnalyticsStore((state) => state.pnlHistory);
  const fetchPnLHistory = useAnalyticsStore((state) => state.fetchPnLHistory);
  const isLoading = useAnalyticsStore((state) => state.isLoading);

  useEffect(() => {
    fetchPnLHistory();
  }, [fetchPnLHistory]);

  if (isLoading && pnlHistory.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>PnL Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] flex items-center justify-center">
            <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (pnlHistory.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>PnL Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] flex items-center justify-center text-muted-foreground">
            No PnL data available for the selected period
          </div>
        </CardContent>
      </Card>
    );
  }

  // Format data for chart
  const chartData = pnlHistory.map((point) => ({
    timestamp: format(new Date(point.timestamp), 'MMM dd HH:mm'),
    pnl: point.pnl,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Cumulative PnL Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="timestamp"
              className="text-xs"
              tick={{ fill: 'currentColor' }}
            />
            <YAxis
              className="text-xs"
              tick={{ fill: 'currentColor' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px'
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="pnl"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={false}
              name="PnL ($)"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
