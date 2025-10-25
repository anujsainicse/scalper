/**
 * User Menu Component
 * Displays user dropdown with all user-related actions
 */

'use client'

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useTheme } from 'next-themes'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { TelegramConnect } from '@/components/TelegramConnect'
import {
  LogOut,
  Sun,
  Moon,
  ChevronDown,
  Link2,
  User,
} from 'lucide-react'
import toast from 'react-hot-toast'

export function UserMenu() {
  const { user, signOut } = useAuth()
  const { theme, setTheme } = useTheme()
  const [open, setOpen] = useState(false)

  const handleLogout = async () => {
    try {
      await signOut()
      toast.success('Logged out successfully')
    } catch (error: any) {
      console.error('Logout error:', error)
      toast.error(error.message || 'Failed to logout')
    }
  }

  if (!user) {
    return null
  }

  // Get user initial for avatar
  const userInitial = user.email?.charAt(0).toUpperCase() || 'U'

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="flex items-center gap-2 h-10 px-3 hover:bg-accent"
        >
          {/* User Avatar */}
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold text-sm">
            {userInitial}
          </div>
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent className="w-64" align="end" forceMount>
        {/* User Email */}
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">{user.email}</p>
            <p className="text-xs leading-none text-muted-foreground">
              {user.user_metadata?.full_name || 'Trading Bot User'}
            </p>
          </div>
        </DropdownMenuLabel>

        <DropdownMenuSeparator />

        {/* Theme Selector */}
        <div className="px-2 py-2">
          <p className="text-xs font-medium text-muted-foreground mb-2">Theme</p>
          <div className="grid grid-cols-2 gap-2">
            <Button
              variant={theme === 'light' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTheme('light')}
              className="h-8 text-xs"
            >
              <Sun className="h-3 w-3 mr-1" />
              Light
            </Button>
            <Button
              variant={theme === 'dark' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTheme('dark')}
              className="h-8 text-xs"
            >
              <Moon className="h-3 w-3 mr-1" />
              Dark
            </Button>
          </div>
        </div>

        <DropdownMenuSeparator />

        {/* Profile */}
        <DropdownMenuItem className="cursor-pointer">
          <User className="mr-2 h-4 w-4" />
          <span>Profile</span>
        </DropdownMenuItem>

        {/* Exchange Connect */}
        <DropdownMenuItem className="cursor-pointer">
          <Link2 className="mr-2 h-4 w-4" />
          <span>Exchange Connect</span>
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        {/* Telegram Connect - Custom component */}
        <div className="px-2 py-2">
          <TelegramConnect />
        </div>

        <DropdownMenuSeparator />

        <DropdownMenuItem onClick={handleLogout} className="text-red-600 focus:text-red-600">
          <LogOut className="mr-2 h-4 w-4" />
          <span>Log out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
