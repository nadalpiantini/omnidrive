"use client"

import { useState, useEffect } from 'react'
import { filesApi, type FileMetadata } from '@/lib/api'
import { FileIcon, FolderOpen, Cloud, Download, Trash2 } from 'lucide-react'

export default function FilesPage() {
  const [files, setFiles] = useState<FileMetadata[]>([])
  const [selectedService, setSelectedService] = useState<'google' | 'folderfort'>('google')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadFiles()
  }, [selectedService])

  const loadFiles = async () => {
    setLoading(true)
    try {
      const response = await filesApi.list(selectedService)
      setFiles(response.files)
    } catch (error) {
      console.error('Failed to load files:', error)
    } finally {
      setLoading(false)
    }
  }

  const getFileIcon = (mime_type?: string) => {
    if (!mime_type) return <FileIcon className="h-5 w-5 text-gray-400" />
    if (mime_type.includes('folder')) return <FolderOpen className="h-5 w-5 text-blue-500" />
    if (mime_type.includes('pdf')) return <FileIcon className="h-5 w-5 text-red-500" />
    if (mime_type.includes('image')) return <FileIcon className="h-5 w-5 text-green-500" />
    if (mime_type.includes('video')) return <FileIcon className="h-5 w-5 text-purple-500" />
    return <FileIcon className="h-5 w-5 text-gray-400" />
  }

  const formatSize = (bytes?: number) => {
    if (!bytes) return '-'
    const units = ['B', 'KB', 'MB', 'GB']
    let size = bytes
    let unitIndex = 0
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024
      unitIndex++
    }
    return `${size.toFixed(1)} ${units[unitIndex]}`
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Files</h1>
            <p className="text-gray-600 mt-1">Browse and manage your cloud storage</p>
          </div>

          {/* Service Selector */}
          <div className="flex gap-2">
            <button
              onClick={() => setSelectedService('google')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedService === 'google'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Google Drive
            </button>
            <button
              onClick={() => setSelectedService('folderfort')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedService === 'folderfort'
                  ? 'bg-purple-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Folderfort
            </button>
          </div>
        </div>

        {/* Files List */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Size
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {files.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-gray-500">
                      <Cloud className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>No files found</p>
                    </td>
                  </tr>
                ) : (
                  files.map((file) => (
                    <tr key={file.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getFileIcon(file.mime_type)}
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{file.name}</div>
                              {file.parent_id && (
                                <div className="text-xs text-gray-500">ID: {file.id}</div>
                              )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatSize(file.size)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {file.mime_type || 'Unknown'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end gap-2">
                          <button className="text-blue-600 hover:text-blue-900">
                            <Download className="h-4 w-4" />
                          </button>
                          <button className="text-red-600 hover:text-red-900">
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
