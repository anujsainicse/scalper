import { BotConfiguration } from '@/components/BotConfiguration';
import { ActiveBots } from '@/components/ActiveBots';
import { ActivityLog } from '@/components/ActivityLog';
import { ThemeToggle } from '@/components/ThemeToggle';
import { TelegramConnect } from '@/components/TelegramConnect';

export default function Home() {
  return (
    <div className="min-h-screen p-4 md:p-6">
      {/* Header */}
      <header className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            Scalper Bot Dashboard
          </h1>
          <p className="text-muted-foreground">
            Configure and manage your cryptocurrency scalping bots
          </p>
        </div>
        <div className="flex items-center gap-2">
          <TelegramConnect />
          <ThemeToggle />
        </div>
      </header>

      {/* Main Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-[calc(100vh-180px)]">
        {/* Left Panel - Bot Configuration */}
        <div className="lg:col-span-4 overflow-y-auto">
          <BotConfiguration />
        </div>

        {/* Right Panel - Active Bots */}
        <div className="lg:col-span-8 overflow-y-auto">
          <ActiveBots />
        </div>
      </div>

      {/* Bottom Panel - Activity Log */}
      <div className="mt-4 h-[280px]">
        <ActivityLog />
      </div>
    </div>
  );
}
