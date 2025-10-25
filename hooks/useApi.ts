/**
 * useApi Hook
 * Initializes API client with authentication token
 */

'use client'

import { useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { api } from '@/lib/api'

export function useApi() {
  const { getAccessToken } = useAuth()

  useEffect(() => {
    // Set the access token getter on the API client
    api.setAccessTokenGetter(getAccessToken)
  }, [getAccessToken])

  return api
}
