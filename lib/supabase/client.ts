/**
 * Supabase Client Configuration
 * Browser-side Supabase client for authentication
 */

import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  console.log('[Supabase Client] URL:', supabaseUrl ? '✅ Set' : '❌ Not set')
  console.log('[Supabase Client] Anon Key:', supabaseAnonKey ? '✅ Set' : '❌ Not set')

  if (!supabaseUrl || !supabaseAnonKey) {
    console.warn('⚠️ Supabase credentials not configured. Authentication disabled.')
    // Return a mock client for development without Supabase
    return null
  }

  console.log('✅ Supabase client initialized successfully')
  return createBrowserClient(supabaseUrl, supabaseAnonKey)
}
