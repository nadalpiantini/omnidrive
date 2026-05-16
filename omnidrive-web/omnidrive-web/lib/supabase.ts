import { createClient, type SupabaseClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://nqzhxukuvmdlpewqytpv.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || ''

// Lazy initialization — avoid throwing at module-eval time when env vars are
// missing (e.g. during `next build` static analysis on Vercel). Routes that
// actually need Supabase call the factory at request time and get a clear
// runtime error if the key isn't configured.
let _supabase: SupabaseClient | null = null
let _supabaseAdmin: SupabaseClient | null = null

export function getSupabase(): SupabaseClient {
  if (!_supabase) {
    if (!supabaseAnonKey) {
      throw new Error(
        'Supabase anon key missing — set NEXT_PUBLIC_SUPABASE_ANON_KEY in your environment.'
      )
    }
    _supabase = createClient(supabaseUrl, supabaseAnonKey)
  }
  return _supabase
}

export function getSupabaseAdmin(): SupabaseClient {
  if (!_supabaseAdmin) {
    if (!supabaseServiceKey) {
      throw new Error(
        'Supabase service key missing — set SUPABASE_SERVICE_ROLE_KEY in your environment.'
      )
    }
    _supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey)
  }
  return _supabaseAdmin
}

// Back-compat proxies — accessing properties triggers lazy init. Lets existing
// `import { supabase, supabaseAdmin } from '@/lib/supabase'` keep working
// without forcing route-level refactors.
export const supabase = new Proxy({} as SupabaseClient, {
  get(_target, prop) {
    return (getSupabase() as unknown as Record<string | symbol, unknown>)[prop]
  },
})

export const supabaseAdmin = new Proxy({} as SupabaseClient, {
  get(_target, prop) {
    return (getSupabaseAdmin() as unknown as Record<string | symbol, unknown>)[prop]
  },
})

export interface OmnidriveFile {
  id: string
  service: string
  file_id: string
  name: string
  mime_type?: string
  size?: number
  parent_id?: string
  created_at: string
  modified_at: string
  metadata: Record<string, unknown>
}

export interface OmnidriveSyncJob {
  id: string
  source_service: string
  target_service: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  files_synced: number
  total_files: number
  error_message?: string
  started_at: string
  completed_at?: string
  metadata: Record<string, unknown>
}

export interface OmnidriveAuthConfig {
  id: string
  service: string
  user_id?: string
  encrypted_credentials?: string
  created_at: string
  updated_at: string
  is_active: boolean
}
