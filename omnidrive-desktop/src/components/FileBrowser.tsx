import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Download,
  Trash2,
  Upload,
  RefreshCw,
  Grid,
  List,
  FolderOpen,
  Eye,
} from 'lucide-react'
import FileIcon from './FileIcon'
import FilePreview from './FilePreview'

interface FileBrowserProps {
  service: 'google' | 'folderfort'
}

interface FileItem {
  id: string
  name: string
  type: 'file' | 'folder'
  size?: string
  mimeType?: string
  modified?: string
}

function parseFileList(stdout: string): FileItem[] {
  const lines = stdout.split('\n')
  const files: FileItem[] = []
  let currentFile: Partial<FileItem> | null = null

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (line.includes('Files (showing') || line.startsWith('---') || !line.trim()) continue

    const idMatch = line.match(/ID:\s*([^\s|]+)/)
    if (idMatch) {
      const sizeMatch = line.match(/Size:\s*([\d.]+\s*[KMGT]?B)/)
      if (currentFile) {
        currentFile.id = idMatch[1]
        if (sizeMatch) currentFile.size = sizeMatch[1]
      }
      continue
    }

    const trimmed = line.trim()
    if (trimmed && !trimmed.startsWith('ID:')) {
      if (currentFile?.id && currentFile?.name) {
        files.push(currentFile as FileItem)
      }
      const nameOnly = trimmed.replace(/^[\u{1F300}-\u{1F9FF}][\u{FE00}-\u{FE0F}]?\s*/u, '').trim()
      const isFolder = /[\u{1F4C1}\u{1F4C2}]/u.test(trimmed)
      currentFile = {
        id: '',
        name: nameOnly || trimmed,
        type: isFolder ? 'folder' : 'file',
      }
    }
  }

  if (currentFile?.id && currentFile?.name) {
    files.push(currentFile as FileItem)
  }

  return files
}

export default function FileBrowser({ service }: FileBrowserProps) {
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [previewFile, setPreviewFile] = useState<FileItem | null>(null)
  const [downloading, setDownloading] = useState<string | null>(null)
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' | 'info' } | null>(null)

  const showMessage = (text: string, type: 'success' | 'error' | 'info' = 'info') => {
    setMessage({ text, type })
    setTimeout(() => setMessage(null), 4000)
  }

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['files', service],
    queryFn: async () => {
      if (typeof window.omnidrive === 'undefined') {
        throw new Error('OmniDrive API not available')
      }
      const result = await window.omnidrive.list(service, 100)
      if (result.code !== 0) {
        throw new Error(result.stderr || 'Failed to list files')
      }
      return parseFileList(result.stdout)
    },
    staleTime: 30000,
    retry: 1,
  })

  const files = data || []

  const toggleSelection = (id: string, e?: React.MouseEvent) => {
    if (e?.shiftKey) {
      // Multi-select
      setSelectedFiles(prev =>
        prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id]
      )
    } else {
      setSelectedFiles(prev => prev.includes(id) ? [] : [id])
    }
  }

  const handleDownload = async (file: FileItem) => {
    if (typeof window.omnidrive === 'undefined') return

    // Ask for download location
    const destFolder = await window.omnidrive.selectFolder()
    if (!destFolder) return

    setDownloading(file.id)
    showMessage(`Downloading ${file.name}...`, 'info')

    const result = await window.omnidrive.download(service, file.id, destFolder)
    setDownloading(null)

    if (result.code === 0) {
      const downloadedPath = result.stdout.match(/Downloaded to:\s*(.+)/)?.[1]?.trim()
      showMessage(`Downloaded: ${file.name}`, 'success')

      // Offer to show in finder
      if (downloadedPath) {
        setTimeout(() => {
          window.omnidrive.showInFolder(downloadedPath)
        }, 500)
      }
    } else {
      if (result.stderr.includes('fileNotDownloadable')) {
        showMessage('Google Doc - open in browser to export', 'error')
      } else {
        showMessage(`Download failed: ${result.stderr.slice(0, 100)}`, 'error')
      }
    }
  }

  const handleDelete = async (file: FileItem) => {
    if (typeof window.omnidrive === 'undefined') return
    if (!confirm(`Delete "${file.name}"? This will move it to trash.`)) return

    showMessage(`Deleting ${file.name}...`, 'info')
    const result = await window.omnidrive.delete(service, file.id)

    if (result.code === 0) {
      showMessage(`Deleted: ${file.name}`, 'success')
      refetch()
    } else {
      showMessage(`Delete failed: ${result.stderr.slice(0, 100)}`, 'error')
    }
    setPreviewFile(null)
  }

  const handleUpload = async () => {
    // TODO: Implement native file picker and upload
    showMessage('Upload coming soon!', 'info')
  }

  return (
    <div className="h-full flex flex-col">
      {/* Toast Message */}
      {message && (
        <div className={`fixed top-20 right-4 z-50 px-4 py-3 rounded-lg shadow-lg text-sm flex items-center gap-2 ${
          message.type === 'success' ? 'bg-green-900/90 border border-green-700 text-green-100' :
          message.type === 'error' ? 'bg-red-900/90 border border-red-700 text-red-100' :
          'bg-gray-800/90 border border-gray-700 text-gray-100'
        }`}>
          {message.text}
        </div>
      )}

      {/* Preview Modal */}
      {previewFile && (
        <FilePreview
          file={previewFile}
          onClose={() => setPreviewFile(null)}
          onDownload={() => handleDownload(previewFile)}
          onDelete={() => handleDelete(previewFile)}
          isDownloading={downloading === previewFile.id}
        />
      )}

      {/* Toolbar */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <button
            onClick={handleUpload}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg text-sm font-medium transition-colors"
          >
            <Upload className="w-4 h-4" />
            Upload
          </button>
          <button
            onClick={() => refetch()}
            disabled={isLoading}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="flex items-center gap-4">
          {/* View Toggle */}
          <div className="flex items-center bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded ${viewMode === 'grid' ? 'bg-gray-700' : 'hover:bg-gray-700/50'}`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-1.5 rounded ${viewMode === 'list' ? 'bg-gray-700' : 'hover:bg-gray-700/50'}`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>

          <div className="text-sm text-gray-400">
            {files.length} items
            {selectedFiles.length > 0 && (
              <span className="ml-2 text-primary-400">
                ({selectedFiles.length} selected)
              </span>
            )}
          </div>
        </div>
      </div>

      {/* File Display */}
      {error ? (
        <div className="flex-1 flex flex-col items-center justify-center text-red-400">
          <p className="mb-4">Error loading files</p>
          <p className="text-sm text-gray-500">{(error as Error).message}</p>
          <button
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg"
          >
            Try Again
          </button>
        </div>
      ) : isLoading ? (
        <div className="flex-1 flex items-center justify-center text-gray-400">
          <RefreshCw className="w-8 h-8 animate-spin mr-3" />
          <span className="text-lg">Loading files...</span>
        </div>
      ) : files.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
          <FolderOpen className="w-16 h-16 mb-4 opacity-50" />
          <p>No files found</p>
        </div>
      ) : viewMode === 'grid' ? (
        /* Grid View */
        <div className="flex-1 overflow-auto">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
            {files.map((file) => (
              <div
                key={file.id}
                onClick={(e) => toggleSelection(file.id, e)}
                onDoubleClick={() => setPreviewFile(file)}
                className={`group relative p-4 rounded-xl border-2 transition-all cursor-pointer ${
                  selectedFiles.includes(file.id)
                    ? 'border-primary-500 bg-primary-500/10 shadow-lg shadow-primary-500/20'
                    : 'border-transparent hover:border-gray-700 bg-gray-800/30 hover:bg-gray-800/60'
                }`}
              >
                {/* File Icon */}
                <div className="flex justify-center mb-3">
                  <FileIcon name={file.name} mimeType={file.mimeType} isFolder={file.type === 'folder'} size="lg" />
                </div>

                {/* File Name */}
                <div className="text-sm font-medium truncate text-center" title={file.name}>
                  {file.name}
                </div>

                {/* Size */}
                {file.size && (
                  <div className="text-xs text-gray-500 mt-1 text-center">{file.size}</div>
                )}

                {/* Quick Actions Overlay */}
                <div className="absolute inset-0 bg-gray-900/80 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                  <button
                    onClick={(e) => { e.stopPropagation(); setPreviewFile(file) }}
                    className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
                    title="Preview"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  {file.type === 'file' && (
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDownload(file) }}
                      disabled={downloading === file.id}
                      className="p-2 bg-primary-600 hover:bg-primary-700 rounded-lg disabled:opacity-50"
                      title="Download"
                    >
                      <Download className={`w-4 h-4 ${downloading === file.id ? 'animate-bounce' : ''}`} />
                    </button>
                  )}
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDelete(file) }}
                    className="p-2 bg-red-600/80 hover:bg-red-600 rounded-lg"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        /* List View */
        <div className="flex-1 overflow-auto">
          <table className="w-full">
            <thead className="sticky top-0 bg-gray-900 border-b border-gray-800">
              <tr className="text-left text-sm text-gray-400">
                <th className="p-3 font-medium">Name</th>
                <th className="p-3 font-medium w-24">Size</th>
                <th className="p-3 font-medium w-32">Actions</th>
              </tr>
            </thead>
            <tbody>
              {files.map((file) => (
                <tr
                  key={file.id}
                  onClick={(e) => toggleSelection(file.id, e)}
                  onDoubleClick={() => setPreviewFile(file)}
                  className={`border-b border-gray-800/50 cursor-pointer transition-colors ${
                    selectedFiles.includes(file.id)
                      ? 'bg-primary-500/10'
                      : 'hover:bg-gray-800/50'
                  }`}
                >
                  <td className="p-3">
                    <div className="flex items-center gap-3">
                      <FileIcon name={file.name} mimeType={file.mimeType} isFolder={file.type === 'folder'} size="sm" />
                      <span className="truncate max-w-md">{file.name}</span>
                    </div>
                  </td>
                  <td className="p-3 text-sm text-gray-400">{file.size || '-'}</td>
                  <td className="p-3">
                    <div className="flex items-center gap-1">
                      <button
                        onClick={(e) => { e.stopPropagation(); setPreviewFile(file) }}
                        className="p-1.5 hover:bg-gray-700 rounded"
                        title="Preview"
                      >
                        <Eye className="w-4 h-4 text-gray-400" />
                      </button>
                      {file.type === 'file' && (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleDownload(file) }}
                          disabled={downloading === file.id}
                          className="p-1.5 hover:bg-gray-700 rounded disabled:opacity-50"
                          title="Download"
                        >
                          <Download className={`w-4 h-4 text-gray-400 ${downloading === file.id ? 'animate-bounce' : ''}`} />
                        </button>
                      )}
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDelete(file) }}
                        className="p-1.5 hover:bg-red-900/50 rounded"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4 text-gray-400 hover:text-red-400" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
