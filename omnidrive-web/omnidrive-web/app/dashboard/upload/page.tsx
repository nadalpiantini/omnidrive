"use client"

import { useState } from 'react'
import { filesApi } from '@/lib/api'
import { Upload, ArrowLeft } from 'lucide-react'
import Link from 'next/link'

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [service, setService] = useState('google')
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null)

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setResult(null)
    try {
      await filesApi.upload(file, service)
      setResult({ success: true, message: `Uploaded ${file.name} to ${service}` })
      setFile(null)
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : 'Upload failed'
      setResult({ success: false, message: msg })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-4">
          <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="text-xl font-bold text-gray-900">Upload Files</h1>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Service</label>
            <select
              value={service}
              onChange={(e) => setService(e.target.value)}
              className="w-full border rounded-lg px-3 py-2"
            >
              <option value="google">Google Drive</option>
              <option value="folderfort">Folderfort</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">File</label>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full border rounded-lg px-3 py-2"
            />
          </div>

          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="w-full bg-blue-600 text-white rounded-lg px-4 py-2 flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Upload className="h-4 w-4" />
            {uploading ? 'Uploading...' : 'Upload'}
          </button>

          {result && (
            <div className={`p-4 rounded-lg ${result.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {result.message}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
