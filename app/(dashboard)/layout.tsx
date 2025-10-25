'use client'

import { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { Sidebar } from '@/components/layout/Sidebar'
import { UserMenu } from '@/components/UserMenu'
import { cn } from '@/lib/utils'

// Bot type configurations
const BOT_CONFIGS: Record<string, { title: string; gradient: string }> = {
  '/home': {
    title: 'Home',
    gradient: 'from-blue-500 to-cyan-500'
  },
  '/scalper': {
    title: 'Scalper Bot',
    gradient: 'from-green-500 via-blue-500 to-purple-500 dark:from-green-400 dark:via-blue-400 dark:to-purple-400'
  },
  '/grid': {
    title: 'Grid Bot',
    gradient: 'from-blue-500 to-purple-500'
  },
  '/dca': {
    title: 'DCA Bot',
    gradient: 'from-purple-500 to-pink-500'
  },
  '/dip': {
    title: 'Dip Bot',
    gradient: 'from-pink-500 to-red-500'
  },
  '/momentum': {
    title: 'Momentum Bot',
    gradient: 'from-orange-500 to-yellow-500'
  },
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(true)
  const pathname = usePathname()

  // Get current bot config based on pathname
  const currentBotConfig = BOT_CONFIGS[pathname || '/scalper'] || BOT_CONFIGS['/scalper']

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {/* Main Content Area */}
      <div className={cn(
        "flex-1 transition-all duration-300",
        isSidebarCollapsed ? "ml-16" : "ml-64"
      )}>
        {/* Header */}
        <header className="sticky top-0 z-30 bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60 border-b border-border">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                className="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-accent transition-colors"
                title={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
              >
                {isSidebarCollapsed ? (
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                ) : (
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                )}
              </button>
              <h1 className={cn(
                "text-2xl font-bold bg-gradient-to-r bg-clip-text text-transparent",
                currentBotConfig.gradient
              )}>
                {currentBotConfig.title}
              </h1>
            </div>
            <UserMenu />
          </div>
        </header>

        {/* Page Content */}
        <main className="min-h-[calc(100vh-73px)]">
          {children}
        </main>
      </div>
    </div>
  )
}
