import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://nqzhxukuvmdlpewqytpv.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || ''

// Client-side Supabase client (uses anon key)
export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Server-side Supabase client (uses service role key)
export const supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey)

// Database types
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
  metadata: Record<string, any>
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
  metadata: Record<string, any>
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
