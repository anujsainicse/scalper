'use client';

import { ProtectedRoute } from '@/components/ProtectedRoute';
import { DataLoader } from '@/components/DataLoader';

export default function GridBotPage() {
  return (
    <ProtectedRoute>
      <DataLoader>
        <div className="p-4 md:p-6">
          <div className="bg-card border border-border rounded-xl p-8 text-center">
            <div className="mb-4">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
                Grid Bot
              </h1>
              <p className="text-muted-foreground mb-6">
                Automated grid trading strategy - Coming Soon
              </p>
            </div>
            <div className="max-w-2xl mx-auto text-left space-y-4 text-muted-foreground">
              <p>
                Grid trading bots place buy and sell orders at regular intervals within a price range,
                profiting from market volatility.
              </p>
              <div className="bg-muted/50 rounded-lg p-4">
                <h3 className="font-semibold mb-2 text-foreground">Features (Coming Soon):</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li>Configurable price range and grid levels</li>
                  <li>Automatic buy low, sell high execution</li>
                  <li>Dynamic grid adjustment based on volatility</li>
                  <li>Multiple grid strategies (Arithmetic, Geometric)</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </DataLoader>
    </ProtectedRoute>
  );
}
