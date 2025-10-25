'use client';

import { ProtectedRoute } from '@/components/ProtectedRoute';
import { DataLoader } from '@/components/DataLoader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useRouter } from 'next/navigation';
import {
  Zap,
  Grid3x3,
  TrendingDown,
  TrendingUp,
  Rocket,
  ArrowRight,
  Activity,
  DollarSign,
  TrendingUpIcon,
} from 'lucide-react';

const BOT_TYPES = [
  {
    id: 'scalper',
    name: 'Scalper Bot',
    icon: Zap,
    path: '/scalper',
    gradient: 'from-green-500 to-blue-500',
    description: 'Quick buy/sell trades for rapid profit in volatile markets',
    status: 'Active',
  },
  {
    id: 'grid',
    name: 'Grid Bot',
    icon: Grid3x3,
    path: '/grid',
    gradient: 'from-blue-500 to-purple-500',
    description: 'Automated grid trading strategy for range-bound markets',
    status: 'Coming Soon',
  },
  {
    id: 'dca',
    name: 'DCA Bot',
    icon: TrendingDown,
    path: '/dca',
    gradient: 'from-purple-500 to-pink-500',
    description: 'Dollar-cost averaging for long-term investment strategies',
    status: 'Coming Soon',
  },
  {
    id: 'dip',
    name: 'Dip Bot',
    icon: TrendingUp,
    path: '/dip',
    gradient: 'from-pink-500 to-red-500',
    description: 'Automatically buy during price dips and sell on recovery',
    status: 'Coming Soon',
  },
  {
    id: 'momentum',
    name: 'Momentum Bot',
    icon: Rocket,
    path: '/momentum',
    gradient: 'from-orange-500 to-yellow-500',
    description: 'Ride strong price trends with momentum-based entries',
    status: 'Coming Soon',
  },
];

export default function HomePage() {
  const router = useRouter();

  return (
    <ProtectedRoute>
      <DataLoader>
        <div className="p-6 space-y-6">
          {/* Welcome Section */}
          <div className="space-y-2">
            <h2 className="text-3xl font-bold">Welcome to Trading Bot Platform</h2>
            <p className="text-muted-foreground text-lg">
              Choose a bot type to start automating your trading strategies
            </p>
          </div>

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Total Bots</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0</div>
                <p className="text-xs text-muted-foreground">Active trading bots</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Total PnL</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">$0.00</div>
                <p className="text-xs text-muted-foreground">All-time profit/loss</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Today's Performance</CardTitle>
                <TrendingUpIcon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0%</div>
                <p className="text-xs text-muted-foreground">Daily return</p>
              </CardContent>
            </Card>
          </div>

          {/* Bot Types Grid */}
          <div>
            <h3 className="text-xl font-semibold mb-4">Available Bot Types</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {BOT_TYPES.map((bot) => {
                const Icon = bot.icon;
                const isActive = bot.status === 'Active';

                return (
                  <Card
                    key={bot.id}
                    className={`group cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-105 ${
                      !isActive ? 'opacity-75' : ''
                    }`}
                    onClick={() => isActive && router.push(bot.path)}
                  >
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div
                          className={`p-3 rounded-lg bg-gradient-to-r ${bot.gradient} text-white`}
                        >
                          <Icon className="h-6 w-6" />
                        </div>
                        {isActive ? (
                          <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-foreground transition-colors" />
                        ) : (
                          <span className="text-xs bg-muted px-2 py-1 rounded-full">
                            {bot.status}
                          </span>
                        )}
                      </div>
                      <CardTitle className="text-lg mt-4">{bot.name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">{bot.description}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* Quick Start Guide */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Start Guide</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs font-bold">
                  1
                </div>
                <div>
                  <p className="font-medium">Choose a Bot Type</p>
                  <p className="text-sm text-muted-foreground">
                    Select from Scalper, Grid, DCA, Dip, or Momentum bots based on your strategy
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs font-bold">
                  2
                </div>
                <div>
                  <p className="font-medium">Configure Your Bot</p>
                  <p className="text-sm text-muted-foreground">
                    Set trading parameters like ticker, exchange, prices, and quantities
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs font-bold">
                  3
                </div>
                <div>
                  <p className="font-medium">Start Trading</p>
                  <p className="text-sm text-muted-foreground">
                    Deploy your bot and monitor its performance in real-time
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </DataLoader>
    </ProtectedRoute>
  );
}
