'use client';

import { ProtectedRoute } from '@/components/ProtectedRoute';
import { DataLoader } from '@/components/DataLoader';

export default function DCABotPage() {
  return (
    <ProtectedRoute>
      <DataLoader>
        <div className="p-4 md:p-6">
          <div className="bg-card border border-border rounded-xl p-8 text-center">
            <div className="mb-4">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text text-transparent">
                DCA Bot
              </h1>
              <p className="text-muted-foreground mb-6">
                Dollar-Cost Averaging strategy - Coming Soon
              </p>
            </div>
            <div className="max-w-2xl mx-auto text-left space-y-4 text-muted-foreground">
              <p>
                DCA (Dollar-Cost Averaging) bots invest fixed amounts at regular intervals,
                reducing the impact of volatility on your portfolio.
              </p>
              <div className="bg-muted/50 rounded-lg p-4">
                <h3 className="font-semibold mb-2 text-foreground">Features (Coming Soon):</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li>Scheduled recurring investments</li>
                  <li>Customizable investment intervals (hourly, daily, weekly)</li>
                  <li>Smart entry timing based on market conditions</li>
                  <li>Portfolio rebalancing options</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </DataLoader>
    </ProtectedRoute>
  );
}
