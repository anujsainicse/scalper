/**
 * Sidebar Navigation Component
 * Collapsible sidebar for navigating between different bot types
 */

'use client'

import { useState } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import {
  Zap,
  Grid3x3,
  TrendingDown,
  TrendingUp,
  Rocket,
  Home,
  Menu,
} from 'lucide-react'

interface BotType {
  id: string
  name: string
  icon: React.ComponentType<{ className?: string }>
  path: string
  gradient: string
  description: string
}

const BOT_TYPES: BotType[] = [
  {
    id: 'scalper',
    name: 'Scalper Bot',
    icon: Zap,
    path: '/scalper',
    gradient: 'from-green-500 to-blue-500',
    description: 'Quick buy/sell trades',
  },
  {
    id: 'grid',
    name: 'Grid Bot',
    icon: Grid3x3,
    path: '/grid',
    gradient: 'from-blue-500 to-purple-500',
    description: 'Grid trading strategy',
  },
  {
    id: 'dca',
    name: 'DCA Bot',
    icon: TrendingDown,
    path: '/dca',
    gradient: 'from-purple-500 to-pink-500',
    description: 'Dollar-cost averaging',
  },
  {
    id: 'dip',
    name: 'Dip Bot',
    icon: TrendingUp,
    path: '/dip',
    gradient: 'from-pink-500 to-red-500',
    description: 'Buy the dip strategy',
  },
  {
    id: 'momentum',
    name: 'Momentum Bot',
    icon: Rocket,
    path: '/momentum',
    gradient: 'from-orange-500 to-yellow-500',
    description: 'Momentum trading',
  },
]

interface SidebarProps {
  isCollapsed: boolean
  onToggle: () => void
}

export function Sidebar({ isCollapsed, onToggle }: SidebarProps) {
  const pathname = usePathname()
  const router = useRouter()

  const navigateToBot = (path: string) => {
    router.push(path)
  }

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen bg-card border-r border-border transition-all duration-300 ease-in-out',
        isCollapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-center p-4 border-b border-border">
        {!isCollapsed && (
          <h2 className="text-lg font-semibold bg-gradient-to-r from-green-500 to-blue-500 bg-clip-text text-transparent">
            Trading Bots
          </h2>
        )}
        {isCollapsed && (
          <Menu className="h-5 w-5 text-muted-foreground" />
        )}
      </div>

      {/* Navigation Items */}
      <nav className="p-2 space-y-1">
        {/* Home Button */}
        <button
          onClick={() => router.push('/home')}
          className={cn(
            'w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200',
            pathname === '/home'
              ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg'
              : 'hover:bg-muted text-muted-foreground hover:text-foreground',
            isCollapsed ? 'justify-center' : ''
          )}
          title={isCollapsed ? 'Home' : ''}
        >
          <Home className={cn('h-5 w-5 flex-shrink-0')} />
          {!isCollapsed && (
            <div className="flex flex-col items-start flex-1">
              <span className="font-medium text-sm">Home</span>
              <span
                className={cn(
                  'text-xs',
                  pathname === '/home' ? 'text-white/80' : 'text-muted-foreground'
                )}
              >
                Dashboard overview
              </span>
            </div>
          )}
        </button>

        {BOT_TYPES.map((bot) => {
          const Icon = bot.icon
          const isActive = pathname?.startsWith(bot.path)

          return (
            <button
              key={bot.id}
              onClick={() => navigateToBot(bot.path)}
              className={cn(
                'w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200',
                isActive
                  ? `bg-gradient-to-r ${bot.gradient} text-white shadow-lg`
                  : 'hover:bg-muted text-muted-foreground hover:text-foreground',
                isCollapsed ? 'justify-center' : ''
              )}
              title={isCollapsed ? bot.name : ''}
            >
              <Icon className={cn('h-5 w-5 flex-shrink-0', isActive ? '' : '')} />
              {!isCollapsed && (
                <div className="flex flex-col items-start flex-1">
                  <span className="font-medium text-sm">{bot.name}</span>
                  <span
                    className={cn(
                      'text-xs',
                      isActive ? 'text-white/80' : 'text-muted-foreground'
                    )}
                  >
                    {bot.description}
                  </span>
                </div>
              )}
            </button>
          )
        })}
      </nav>

    </aside>
  )
}
