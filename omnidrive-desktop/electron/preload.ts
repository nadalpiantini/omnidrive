import { contextBridge, ipcRenderer } from 'electron'

// Type definitions for the API
interface CLIResult {
  stdout: string
  stderr: string
  code: number
}

interface AuthStatus {
  google: boolean
  folderfort: boolean
}

// Expose a safe API to the renderer process
contextBridge.exposeInMainWorld('omnidrive', {
  // File operations
  list: (service: string, limit?: number): Promise<CLIResult> =>
    ipcRenderer.invoke('cli:list', service, limit),

  upload: (filePath: string, service: string, parentId?: string): Promise<CLIResult> =>
    ipcRenderer.invoke('cli:upload', filePath, service, parentId),

  download: (service: string, fileId: string, dest?: string): Promise<CLIResult> =>
    ipcRenderer.invoke('cli:download', service, fileId, dest),

  delete: (service: string, fileId: string, permanent?: boolean): Promise<CLIResult> =>
    ipcRenderer.invoke('cli:delete', service, fileId, permanent),

  // Sync operations
  sync: (source: string, target: string, dryRun?: boolean): Promise<CLIResult> =>
    ipcRenderer.invoke('cli:sync', source, target, dryRun),

  // Search operations
  search: (query: string, service?: string, topK?: number): Promise<CLIResult> =>
    ipcRenderer.invoke('cli:search', query, service, topK),

  index: (service: string, limit?: number): Promise<CLIResult> =>
    ipcRenderer.invoke('cli:index', service, limit),

  // Workflow operations
  workflows: (): Promise<CLIResult> =>
    ipcRenderer.invoke('cli:workflows'),

  runWorkflow: (name: string): Promise<CLIResult> =>
    ipcRenderer.invoke('cli:runWorkflow', name),

  // Auth
  authStatus: (): Promise<AuthStatus> =>
    ipcRenderer.invoke('cli:authStatus'),

  // Dialogs
  selectFolder: (): Promise<string | null> =>
    ipcRenderer.invoke('dialog:selectFolder'),

  saveFileAs: (defaultName: string): Promise<string | null> =>
    ipcRenderer.invoke('dialog:saveFile', defaultName),

  // Shell
  openPath: (filePath: string): Promise<string> =>
    ipcRenderer.invoke('shell:openPath', filePath),

  showInFolder: (filePath: string): Promise<void> =>
    ipcRenderer.invoke('shell:showItemInFolder', filePath),
})

// Type augmentation for window.omnidrive
declare global {
  interface Window {
    omnidrive: {
      list: (service: string, limit?: number) => Promise<CLIResult>
      upload: (filePath: string, service: string, parentId?: string) => Promise<CLIResult>
      download: (service: string, fileId: string, dest?: string) => Promise<CLIResult>
      delete: (service: string, fileId: string, permanent?: boolean) => Promise<CLIResult>
      sync: (source: string, target: string, dryRun?: boolean) => Promise<CLIResult>
      search: (query: string, service?: string, topK?: number) => Promise<CLIResult>
      index: (service: string, limit?: number) => Promise<CLIResult>
      workflows: () => Promise<CLIResult>
      runWorkflow: (name: string) => Promise<CLIResult>
      authStatus: () => Promise<AuthStatus>
      selectFolder: () => Promise<string | null>
      saveFileAs: (defaultName: string) => Promise<string | null>
      openPath: (filePath: string) => Promise<string>
      showInFolder: (filePath: string) => Promise<void>
    }
  }
}
