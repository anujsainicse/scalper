/**
 * User Menu Component
 * Displays user info and logout button
 */

'use client'

import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { LogOut, User } from 'lucide-react'
import toast from 'react-hot-toast'

export function UserMenu() {
  const { user, signOut } = useAuth()

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

  return (
    <div className="flex items-center gap-3 bg-card border border-border rounded-lg px-4 py-2">
      <div className="flex items-center gap-2">
        <User className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-medium truncate max-w-[150px]">
          {user.email}
        </span>
      </div>
      <Button
        variant="ghost"
        size="sm"
        onClick={handleLogout}
        className="h-8 w-8 p-0"
        title="Logout"
      >
        <LogOut className="h-4 w-4" />
      </Button>
    </div>
  )
}
