/**
 * API Initializer
 * Sets up the API client with authentication token
 */

'use client'

import { useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { api } from '@/lib/api'

export function ApiInitializer({ children }: { children: React.ReactNode }) {
  const { getAccessToken } = useAuth()

  useEffect(() => {
    // Set the access token getter on the global API client
    api.setAccessTokenGetter(getAccessToken)
    console.log('[ApiInitializer] Access token getter configured')
  }, [getAccessToken])

  return <>{children}</>
}
