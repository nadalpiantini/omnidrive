import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Search, Loader2, X, Sparkles, Command, ArrowRight } from 'lucide-react'
import FileIcon from './FileIcon'

interface SearchResult {
  id: string
  name: string
  service: string
  snippet: string
  score: number
}

function parseSearchResults(stdout: string): SearchResult[] {
  const lines = stdout.split('\n').filter(line => line.trim())
  const results: SearchResult[] = []

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (line.includes('Score:') || line.includes('Match:')) {
      results.push({
        id: `result-${i}`,
        name: line.split(':')[0]?.trim() || `Result ${i + 1}`,
        service: 'google',
        snippet: lines[i + 1]?.trim() || '',
        score: parseFloat(line.match(/[\d.]+/)?.[0] || '0.5'),
      })
    }
  }

  return results
}

export default function SearchBar() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [showResults, setShowResults] = useState(false)
  const [isFocused, setIsFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  // Keyboard shortcut: Cmd/Ctrl + K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }
      if (e.key === 'Escape') {
        setShowResults(false)
        inputRef.current?.blur()
      }
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  const searchMutation = useMutation({
    mutationFn: async (searchQuery: string) => {
      if (typeof window.omnidrive === 'undefined') {
        await new Promise(r => setTimeout(r, 800))
        return [
          { id: '1', name: 'contract_2024.pdf', service: 'google', snippet: '...found in paragraph 3 regarding payment terms...', score: 0.95 },
          { id: '2', name: 'meeting_notes.docx', service: 'google', snippet: '...discussed the terms with legal team...', score: 0.87 },
          { id: '3', name: 'project_brief.pdf', service: 'folderfort', snippet: '...outlined deliverables and timeline...', score: 0.72 },
        ]
      }
      const result = await window.omnidrive.search(searchQuery, undefined, 10)
      if (result.code !== 0) {
        throw new Error(result.stderr)
      }
      return parseSearchResults(result.stdout)
    },
    onSuccess: (data) => {
      setResults(data)
      setShowResults(true)
    },
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      searchMutation.mutate(query)
    }
  }

  const clearSearch = () => {
    setQuery('')
    setResults([])
    setShowResults(false)
  }

  return (
    <div className="relative">
      <form onSubmit={handleSearch} className="relative group">
        {/* Glow effect */}
        <div className={`absolute -inset-0.5 bg-gradient-to-r from-primary-500/50 via-purple-500/50 to-pink-500/50 rounded-2xl blur opacity-0 transition-opacity duration-300 ${isFocused ? 'opacity-100' : 'group-hover:opacity-50'}`} />

        {/* Input container */}
        <div className={`relative flex items-center bg-gray-800/80 backdrop-blur-xl border rounded-xl transition-all duration-300 ${isFocused ? 'border-primary-500/50 bg-gray-800' : 'border-gray-700/50 hover:border-gray-600'}`}>
          {/* AI indicator */}
          <div className="pl-4 pr-2">
            <div className="flex items-center gap-1.5 px-2 py-1 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-lg">
              <Sparkles className="w-3.5 h-3.5 text-purple-400" />
              <span className="text-[10px] font-semibold text-purple-300 uppercase tracking-wider">AI</span>
            </div>
          </div>

          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Search files semantically..."
            className="flex-1 bg-transparent py-3.5 text-white placeholder-gray-500 focus:outline-none text-sm"
          />

          {/* Right side controls */}
          <div className="flex items-center gap-2 pr-4">
            {query && !searchMutation.isPending && (
              <button
                type="button"
                onClick={clearSearch}
                className="p-1.5 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-4 h-4 text-gray-500" />
              </button>
            )}

            {searchMutation.isPending ? (
              <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />
            ) : (
              <div className="flex items-center gap-1 px-2 py-1 bg-gray-700/50 rounded-lg text-gray-500">
                <Command className="w-3 h-3" />
                <span className="text-xs font-medium">K</span>
              </div>
            )}
          </div>
        </div>
      </form>

      {/* Search Results Dropdown */}
      {showResults && (
        <div className="absolute top-full left-0 right-0 mt-3 bg-gray-900/95 backdrop-blur-xl border border-gray-700/50 rounded-2xl shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
          {results.length > 0 ? (
            <>
              <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
                <span className="text-sm font-medium text-gray-400">
                  {results.length} results for "{query}"
                </span>
                <button
                  onClick={clearSearch}
                  className="text-xs text-gray-500 hover:text-white transition-colors"
                >
                  Clear
                </button>
              </div>
              <div className="max-h-80 overflow-auto">
                {results.map((result) => (
                  <div
                    key={result.id}
                    className="flex items-start gap-4 p-4 hover:bg-gray-800/50 cursor-pointer transition-colors border-b border-gray-800/50 last:border-0 group"
                  >
                    <FileIcon name={result.name} size="md" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3">
                        <div className="font-medium text-white group-hover:text-primary-400 transition-colors truncate">
                          {result.name}
                        </div>
                        <div className="shrink-0 px-2 py-0.5 bg-green-500/10 text-green-400 text-xs font-medium rounded-full">
                          {Math.round(result.score * 100)}%
                        </div>
                      </div>
                      <div className="text-sm text-gray-400 truncate mt-1">{result.snippet}</div>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-xs text-gray-600 capitalize">{result.service}</span>
                        <ArrowRight className="w-3 h-3 text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : !searchMutation.isPending ? (
            <div className="p-8 text-center">
              <Search className="w-12 h-12 text-gray-700 mx-auto mb-3" />
              <p className="text-gray-400">No results found for "{query}"</p>
              <p className="text-sm text-gray-600 mt-1">Try different keywords</p>
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
}
