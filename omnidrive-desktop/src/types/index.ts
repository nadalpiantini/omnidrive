// File types
export interface FileItem {
  id: string
  name: string
  type: 'file' | 'folder'
  size?: string
  modified?: string
  mimeType?: string
  parentId?: string
}

// Service types
export type CloudService = 'google' | 'folderfort'

// Sync types
export interface SyncJob {
  id: string
  source: CloudService
  target: CloudService
  status: 'pending' | 'running' | 'completed' | 'failed'
  filesProcessed?: number
  totalFiles?: number
  error?: string
  startedAt: Date
  completedAt?: Date
}

// Search types
export interface SearchResult {
  id: string
  name: string
  service: CloudService
  snippet: string
  score: number
  path?: string
}

// Workflow types
export interface Workflow {
  name: string
  description: string
  steps: string[]
  status: 'idle' | 'running' | 'completed' | 'failed'
}

// Governance types
export interface ApprovalRequest {
  id: string
  action: string
  resource: string
  reason: string
  createdAt: Date
  expiresAt: Date
  status: 'pending' | 'approved' | 'rejected' | 'expired'
}

export interface AuditEntry {
  id: string
  timestamp: Date
  agent: string
  action: string
  resource: string
  status: 'success' | 'failure' | 'blocked'
  details?: string
}

// CLI Result type
export interface CLIResult {
  stdout: string
  stderr: string
  code: number
}

// Auth status
export interface AuthStatus {
  google: boolean
  folderfort: boolean
}
