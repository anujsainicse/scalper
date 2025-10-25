'use client';

import { ProtectedRoute } from '@/components/ProtectedRoute';
import { DataLoader } from '@/components/DataLoader';

export default function MomentumBotPage() {
  return (
    <ProtectedRoute>
      <DataLoader>
        <div className="p-4 md:p-6">
          <div className="bg-card border border-border rounded-xl p-8 text-center">
            <div className="mb-4">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-orange-500 to-yellow-500 flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-orange-500 to-yellow-500 bg-clip-text text-transparent">
                Momentum Bot
              </h1>
              <p className="text-muted-foreground mb-6">
                Momentum trading strategy - Coming Soon
              </p>
            </div>
            <div className="max-w-2xl mx-auto text-left space-y-4 text-muted-foreground">
              <p>
                Momentum bots identify and ride strong price trends,
                entering positions when momentum is building and exiting when it weakens.
              </p>
              <div className="bg-muted/50 rounded-lg p-4">
                <h3 className="font-semibold mb-2 text-foreground">Features (Coming Soon):</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li>RSI, MACD, and momentum indicator tracking</li>
                  <li>Trend strength analysis</li>
                  <li>Dynamic entry and exit signals</li>
                  <li>Customizable momentum thresholds</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </DataLoader>
    </ProtectedRoute>
  );
}
