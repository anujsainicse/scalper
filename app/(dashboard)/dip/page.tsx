'use client';

import { ProtectedRoute } from '@/components/ProtectedRoute';
import { DataLoader } from '@/components/DataLoader';

export default function DipBotPage() {
  return (
    <ProtectedRoute>
      <DataLoader>
        <div className="p-4 md:p-6">
          <div className="bg-card border border-border rounded-xl p-8 text-center">
            <div className="mb-4">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-pink-500 to-red-500 flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-pink-500 to-red-500 bg-clip-text text-transparent">
                Dip Bot
              </h1>
              <p className="text-muted-foreground mb-6">
                Buy the dip strategy - Coming Soon
              </p>
            </div>
            <div className="max-w-2xl mx-auto text-left space-y-4 text-muted-foreground">
              <p>
                Dip bots automatically detect and buy during price dips,
                capitalizing on temporary market downturns.
              </p>
              <div className="bg-muted/50 rounded-lg p-4">
                <h3 className="font-semibold mb-2 text-foreground">Features (Coming Soon):</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li>Configurable dip percentage thresholds</li>
                  <li>Volume confirmation for genuine dips</li>
                  <li>Multiple time frame analysis</li>
                  <li>Automatic recovery target setting</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </DataLoader>
    </ProtectedRoute>
  );
}
