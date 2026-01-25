// API client for OmniDrive backend
import { httpClient } from './http'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Types
export interface FileMetadata {
  id: string
  name: string
  size?: number
  mime_type?: string
  created_time?: string
  modified_time?: string
  parent_id?: string
  service: string
}

export interface AuthStatus {
  google_authenticated: boolean
  folderfort_authenticated: boolean
  google_email?: string
  folderfort_email?: string
}

export interface SyncJob {
  job_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  source: string
  target: string
  files_to_sync: number
  files_synced: number
  started_at?: string
  completed_at?: string
  error?: string
}

export interface SearchResult {
  file_name: string
  service: string
  relevance: number
  snippet?: string
  metadata: Record<string, any>
}

// Auth API
export const authApi = {
  getStatus: async () => {
    const response = await httpClient.get<AuthStatus>(`${API_URL}/api/v1/auth/status`)
    return response.data
  },

  authenticateGoogle: async (serviceAccountJson: string) => {
    const response = await httpClient.post(`${API_URL}/api/v1/auth/google`, {
      service_account_json: serviceAccountJson
    })
    return response.data
  },

  authenticateFolderfort: async (email: string, password: string) => {
    const response = await httpClient.post(`${API_URL}/api/v1/auth/folderfort`, {
      email,
      password
    })
    return response.data
  },

  logout: async () => {
    const response = await httpClient.post(`${API_URL}/api/v1/auth/logout`)
    return response.data
  }
}

// Files API
export const filesApi = {
  list: async (service: string, folderId?: string, limit = 100) => {
    const params = new URLSearchParams({
      service,
      ...(folderId && { folder_id: folderId }),
      limit: limit.toString()
    })
    const response = await httpClient.get(`${API_URL}/api/v1/files/?${params}`)
    return response.data
  },

  upload: async (file: File, service: string, parentId?: string, onProgress?: (progress: number) => void) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('service', service)
    if (parentId) formData.append('parent_id', parentId)

    const response = await httpClient.post(`${API_URL}/api/v1/files/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    })
    return response.data
  },

  download: async (service: string, fileId: string) => {
    const response = await httpClient.get(`${API_URL}/api/v1/files/${fileId}/download?service=${service}`, {
      responseType: 'blob'
    })
    return response.data
  },

  delete: async (service: string, fileId: string, permanent = false) => {
    const response = await httpClient.delete(`${API_URL}/api/v1/files/${fileId}?service=${service}&permanent=${permanent}`)
    return response.data
  }
}

// Sync API
export const syncApi = {
  compare: async (service1: string, service2: string, limit = 100) => {
    const response = await httpClient.post(`${API_URL}/api/v1/sync/compare`, {
      service1,
      service2,
      limit
    })
    return response.data
  },

  startSync: async (source: string, target: string, dryRun = false, limit = 100) => {
    const response = await httpClient.post(`${API_URL}/api/v1/sync`, {
      source,
      target,
      dry_run: dryRun,
      limit
    })
    return response.data
  },

  getStatus: async (jobId: string) => {
    const response = await httpClient.get<SyncJob>(`${API_URL}/api/v1/sync/status/${jobId}`)
    return response.data
  }
}

// Search API
export const searchApi = {
  search: async (query: string, service?: string, topK = 5) => {
    const response = await httpClient.post(`${API_URL}/api/v1/search`, {
      query,
      service,
      top_k: topK
    })
    return response.data
  },

  index: async (service: string, limit = 100) => {
    const response = await httpClient.post(`${API_URL}/api/v1/index`, {
      service,
      limit
    })
    return response.data
  }
}

// Workflows API
export const workflowsApi = {
  list: async () => {
    const response = await httpClient.get(`${API_URL}/api/v1/workflows`)
    return response.data
  },

  run: async (name: string, parameters?: Record<string, any>) => {
    const response = await httpClient.post(`${API_URL}/api/v1/workflows/${name}/run`, {
      parameters
    })
    return response.data
  },

  getStatus: async (name: string, jobId: string) => {
    const response = await httpClient.get(`${API_URL}/api/v1/workflows/${name}/status/${jobId}`)
    return response.data
  }
}
