"use client"

import { useState } from 'react'
import { searchApi } from '@/lib/api'
import { Search, ArrowLeft, AlertTriangle } from 'lucide-react'
import Link from 'next/link'

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [service, setService] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<Array<{
    file_name: string
    service: string
    relevance: number
    snippet?: string
  }>>([])
  const [searched, setSearched] = useState(false)

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setSearched(true)
    try {
      const data = await searchApi.search(query, service || undefined)
      setResults(data.results || [])
    } catch (error: unknown) {
      console.error('Search failed:', error)
      setResults([])
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
          <h1 className="text-xl font-bold text-gray-900">Semantic Search</h1>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <div className="flex gap-2">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search across your files..."
              className="flex-1 border rounded-lg px-3 py-2"
            />
            <select
              value={service}
              onChange={(e) => setService(e.target.value)}
              className="border rounded-lg px-3 py-2"
            >
              <option value="">All services</option>
              <option value="google">Google Drive</option>
              <option value="folderfort">Folderfort</option>
            </select>
            <button
              onClick={handleSearch}
              disabled={loading || !query.trim()}
              className="bg-orange-600 text-white rounded-lg px-4 py-2 flex items-center gap-2 disabled:opacity-50"
            >
              <Search className="h-4 w-4" />
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 shrink-0" />
            <div className="text-sm text-yellow-800">
              <p className="font-medium">Indexing not yet implemented</p>
              <p className="mt-1">
                Semantic search requires files to be indexed first.
                The indexing pipeline is under development.
                Search results will be limited until indexing is enabled.
              </p>
            </div>
          </div>

          {searched && results.length === 0 && !loading && (
            <p className="text-gray-500 text-center py-8">No results found.</p>
          )}

          <div className="space-y-3">
            {results.map((r, i) => (
              <div key={i} className="border rounded-lg p-4 hover:bg-gray-50">
                <p className="font-medium text-gray-900">{r.file_name}</p>
                <p className="text-sm text-gray-500">
                  {r.service} — Relevance: {Math.round(r.relevance)}%
                </p>
                {r.snippet && <p className="text-sm text-gray-600 mt-1">{r.snippet}</p>}
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
