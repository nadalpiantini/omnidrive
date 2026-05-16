"use client"

import { useState } from 'react'
import { syncApi } from '@/lib/api'
import { ArrowLeft, Play } from 'lucide-react'
import Link from 'next/link'

export default function SyncPage() {
  const [source, setSource] = useState('google')
  const [target, setTarget] = useState('folderfort')
  const [dryRun, setDryRun] = useState(true)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{ job_id: string; message: string; files_to_sync: string[] } | null>(null)

  const handleSync = async () => {
    if (source === target) {
      alert('Source and target must be different')
      return
    }
    setLoading(true)
    setResult(null)
    try {
      const data = await syncApi.startSync(source, target, dryRun)
      setResult(data)
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : 'Sync failed'
      alert(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-4">
          <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="text-xl font-bold text-gray-900">Sync Services</h1>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Source</label>
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="google">Google Drive</option>
                <option value="folderfort">Folderfort</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Target</label>
              <select
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="google">Google Drive</option>
                <option value="folderfort">Folderfort</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              id="dryRun"
              type="checkbox"
              checked={dryRun}
              onChange={(e) => setDryRun(e.target.checked)}
              className="rounded"
            />
            <label htmlFor="dryRun" className="text-sm text-gray-700">Dry run (preview only)</label>
          </div>

          <button
            onClick={handleSync}
            disabled={loading}
            className="w-full bg-purple-600 text-white rounded-lg px-4 py-2 flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Play className="h-4 w-4" />
            {loading ? 'Starting...' : dryRun ? 'Preview Sync' : 'Start Sync'}
          </button>

          {result && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="font-medium text-blue-900">{result.message}</p>
              {result.files_to_sync.length > 0 && (
                <ul className="mt-2 text-sm text-blue-800 list-disc list-inside">
                  {result.files_to_sync.slice(0, 10).map((f) => (
                    <li key={f}>{f}</li>
                  ))}
                  {result.files_to_sync.length > 10 && (
                    <li>...and {result.files_to_sync.length - 10} more</li>
                  )}
                </ul>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
