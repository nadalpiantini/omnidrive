'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'

type AuthStatus = {
  google_authenticated: boolean
  folderfort_authenticated: boolean
  google_email: string | null
  folderfort_email: string | null
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000'

export default function HomePage() {
  const [status, setStatus] = useState<AuthStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    fetch(`${API_BASE}/api/v1/auth/status`, { cache: 'no-store' })
      .then((res) => {
        if (!res.ok) throw new Error(`API ${res.status}`)
        return res.json()
      })
      .then((data: AuthStatus) => {
        if (!cancelled) setStatus(data)
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const anyAuth = !!(status?.google_authenticated || status?.folderfort_authenticated)
  const allAuth = !!(status?.google_authenticated && status?.folderfort_authenticated)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            OmniDrive
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-2">
            Multi-cloud storage management for Google Drive and Folderfort
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
            CLI-first. Web dashboard wraps the same Python core.
          </p>

          {/* Honest auth status banner */}
          <div className="max-w-xl mx-auto mb-8">
            {loading && (
              <div className="rounded-lg border border-gray-200 dark:border-gray-700 px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                Checking backend at {API_BASE}…
              </div>
            )}
            {!loading && error && (
              <div className="rounded-lg border border-amber-300 bg-amber-50 dark:border-amber-700 dark:bg-amber-950/40 px-4 py-3 text-sm text-amber-900 dark:text-amber-200 text-left">
                <div className="font-semibold mb-1">Backend not reachable ({error}).</div>
                <div className="font-mono text-xs mb-1">{API_BASE}/api/v1/auth/status</div>
                <div>
                  Start the API:{' '}
                  <code className="font-mono bg-amber-100 dark:bg-amber-900 px-1.5 py-0.5 rounded">
                    cd omnidrive-web/api && uvicorn app.main:app --reload
                  </code>
                </div>
              </div>
            )}
            {!loading && status && (
              <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white/60 dark:bg-gray-800/60 px-4 py-3 text-sm text-left">
                <div className="font-semibold text-gray-900 dark:text-white mb-2">
                  Connected services
                </div>
                <ul className="space-y-1">
                  <li className="flex items-center justify-between">
                    <span className="text-gray-700 dark:text-gray-300">Google Drive</span>
                    <span
                      className={
                        status.google_authenticated
                          ? 'text-green-700 dark:text-green-400 font-medium'
                          : 'text-gray-500 dark:text-gray-400'
                      }
                    >
                      {status.google_authenticated ? '✓ connected' : '— not connected'}
                    </span>
                  </li>
                  <li className="flex items-center justify-between">
                    <span className="text-gray-700 dark:text-gray-300">Folderfort</span>
                    <span
                      className={
                        status.folderfort_authenticated
                          ? 'text-green-700 dark:text-green-400 font-medium'
                          : 'text-gray-500 dark:text-gray-400'
                      }
                    >
                      {status.folderfort_authenticated
                        ? `✓ ${status.folderfort_email ?? 'connected'}`
                        : '— not connected'}
                    </span>
                  </li>
                </ul>
              </div>
            )}
          </div>

          <div className="flex gap-4 justify-center flex-wrap">
            {anyAuth ? (
              <Link
                href="/dashboard"
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Open dashboard
              </Link>
            ) : (
              <Link
                href="/dashboard/auth"
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Connect a drive to start
              </Link>
            )}
            <a
              href="https://github.com/nadalpiantini/omnidrive-cli#cli-quickstart"
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
            >
              Use the CLI
            </a>
          </div>
          {!allAuth && !loading && !error && (
            <p className="mt-4 text-xs text-gray-500 dark:text-gray-400">
              Each cloud service requires a one-time auth step before its features unlock.
            </p>
          )}
        </div>

        {/* Features — honest about what currently ships */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard
            icon="🔐"
            title="Two clouds, one CLI"
            body="Google Drive and Folderfort, list / upload / download / delete from a single tool. Each service authenticates separately."
            ready={anyAuth}
          />
          <FeatureCard
            icon="🔍"
            title="Local semantic search"
            body="Index files into a local ChromaDB collection and search with embeddings. Works offline once indexed."
            ready={true}
            note="Indexing is a separate command — files are not auto-indexed."
          />
          <FeatureCard
            icon="🔄"
            title="Durable sync jobs"
            body="Cross-service sync with persistent job state and retry/backoff. Resume interrupted runs by job ID."
            ready={allAuth}
            note={!allAuth ? 'Requires both Google and Folderfort connected.' : undefined}
          />
        </div>
      </div>
    </div>
  )
}

function FeatureCard({
  icon,
  title,
  body,
  ready,
  note,
}: {
  icon: string
  title: string
  body: string
  ready: boolean
  note?: string
}) {
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-xl font-semibold dark:text-white">
          <span className="mr-2">{icon}</span>
          {title}
        </h3>
        <span
          className={
            ready
              ? 'text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
              : 'text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
          }
        >
          {ready ? 'ready' : 'setup needed'}
        </span>
      </div>
      <p className="text-gray-600 dark:text-gray-300 text-sm">{body}</p>
      {note && (
        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400 italic">{note}</p>
      )}
    </div>
  )
}
