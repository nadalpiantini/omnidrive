import { X, Download, ExternalLink, Trash2 } from 'lucide-react'
import FileIcon from './FileIcon'

interface FilePreviewProps {
  file: {
    id: string
    name: string
    type: 'file' | 'folder'
    size?: string
    mimeType?: string
    modified?: string
  }
  onClose: () => void
  onDownload: () => void
  onDelete: () => void
  isDownloading?: boolean
}

export default function FilePreview({ file, onClose, onDownload, onDelete, isDownloading }: FilePreviewProps) {
  const isGoogleDoc = file.mimeType?.includes('google-apps')
  const isImage = file.name.match(/\.(jpg|jpeg|png|gif|webp|svg)$/i)
  const isPdf = file.name.endsWith('.pdf')

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="bg-gray-900 rounded-xl border border-gray-700 shadow-2xl w-full max-w-2xl mx-4 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <FileIcon name={file.name} mimeType={file.mimeType} isFolder={file.type === 'folder'} size="md" />
            <div>
              <h2 className="font-semibold text-lg truncate max-w-md">{file.name}</h2>
              {file.size && <p className="text-sm text-gray-400">{file.size}</p>}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Preview Area */}
        <div className="h-64 flex items-center justify-center bg-gray-950 p-8">
          {isGoogleDoc ? (
            <div className="text-center">
              <FileIcon name={file.name} mimeType={file.mimeType} size="lg" className="mx-auto mb-4" />
              <p className="text-gray-400 mb-2">Google Workspace Document</p>
              <p className="text-sm text-gray-500">Open in Google Drive to view or edit</p>
            </div>
          ) : isImage ? (
            <div className="text-center">
              <FileIcon name={file.name} size="lg" className="mx-auto mb-4" />
              <p className="text-gray-400">Image preview</p>
              <p className="text-sm text-gray-500">Download to view full image</p>
            </div>
          ) : isPdf ? (
            <div className="text-center">
              <FileIcon name={file.name} size="lg" className="mx-auto mb-4" />
              <p className="text-gray-400">PDF Document</p>
              <p className="text-sm text-gray-500">Download to view</p>
            </div>
          ) : (
            <div className="text-center">
              <FileIcon name={file.name} mimeType={file.mimeType} size="lg" className="mx-auto mb-4" />
              <p className="text-gray-400">{file.name.split('.').pop()?.toUpperCase() || 'File'}</p>
            </div>
          )}
        </div>

        {/* File Info */}
        <div className="p-4 border-t border-gray-800 bg-gray-900/50">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">File ID:</span>
              <p className="text-gray-300 truncate font-mono text-xs">{file.id}</p>
            </div>
            <div>
              <span className="text-gray-500">Size:</span>
              <p className="text-gray-300">{file.size || 'Unknown'}</p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between p-4 border-t border-gray-800 bg-gray-900">
          <button
            onClick={onDelete}
            className="flex items-center gap-2 px-4 py-2 text-red-400 hover:bg-red-900/30 rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            Delete
          </button>

          <div className="flex items-center gap-2">
            {isGoogleDoc ? (
              <a
                href={`https://drive.google.com/file/d/${file.id}/view`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                Open in Drive
              </a>
            ) : (
              <button
                onClick={onDownload}
                disabled={isDownloading}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 rounded-lg transition-colors"
              >
                <Download className={`w-4 h-4 ${isDownloading ? 'animate-bounce' : ''}`} />
                {isDownloading ? 'Downloading...' : 'Download'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
