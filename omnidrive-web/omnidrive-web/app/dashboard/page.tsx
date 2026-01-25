"use client"

import { useEffect, useState } from 'react'
import { authApi, filesApi, type FileMetadata } from '@/lib/api'
import { Cloud, Folder, HardDrive, RefreshCw, Search, Upload } from 'lucide-react'
import Link from 'next/link'

export default function DashboardPage() {
  const [authStatus, setAuthStatus] = useState<any>(null)
  const [stats, setStats] = useState({
    googleFiles: 0,
    folderfortFiles: 0,
    totalFiles: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      // Get auth status
      const status = await authApi.getStatus()
      setAuthStatus(status)

      // Get file counts
      let googleCount = 0
      let folderfortCount = 0

      if (status.google_authenticated) {
        const googleFiles = await filesApi.list('google', undefined, 1)
        googleCount = googleFiles.total
      }

      if (status.folderfort_authenticated) {
        const folderfortFiles = await filesApi.list('folderfort', undefined, 1)
        folderfortCount = folderfortFiles.total
      }

      setStats({
        googleFiles: googleCount,
        folderfortFiles: folderfortCount,
        totalFiles: googleCount + folderfortCount
      })
    } catch (error) {
      console.error('Failed to load dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <HardDrive className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">OmniDrive</h1>
                <p className="text-sm text-gray-500">Multi-cloud storage manager</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                {authStatus?.google_authenticated && '✅ Google'}
                {authStatus?.folderfort_authenticated && ' ✅ Folderfort'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Files</p>
                <p className="text-3xl font-bold text-gray-900">{stats.totalFiles.toLocaleString()}</p>
              </div>
              <Folder className="h-12 w-12 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Google Drive</p>
                <p className="text-3xl font-bold text-green-600">{stats.googleFiles.toLocaleString()}</p>
              </div>
              <Cloud className="h-12 w-12 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Folderfort</p>
                <p className="text-3xl font-bold text-purple-600">{stats.folderfortFiles.toLocaleString()}</p>
              </div>
              <Cloud className="h-12 w-12 text-purple-600" />
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link href="/dashboard/files" className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
            <Folder className="h-8 w-8 text-blue-600 mb-3" />
            <h3 className="font-semibold text-gray-900">Browse Files</h3>
            <p className="text-sm text-gray-500 mt-1">Explore your cloud storage</p>
          </Link>

          <Link href="/dashboard/upload" className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
            <Upload className="h-8 w-8 text-green-600 mb-3" />
            <h3 className="font-semibold text-gray-900">Upload Files</h3>
            <p className="text-sm text-gray-500 mt-1">Upload to any service</p>
          </Link>

          <Link href="/dashboard/sync" className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
            <RefreshCw className="h-8 w-8 text-purple-600 mb-3" />
            <h3 className="font-semibold text-gray-900">Sync Services</h3>
            <p className="text-sm text-gray-500 mt-1">Sync between drives</p>
          </Link>

          <Link href="/dashboard/search" className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
            <Search className="h-8 w-8 text-orange-600 mb-3" />
            <h3 className="font-semibold text-gray-900">Semantic Search</h3>
            <p className="text-sm text-gray-500 mt-1">Search in file contents</p>
          </Link>
        </div>

        {/* Auth Status */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Connected Services</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${authStatus?.google_authenticated ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className="font-medium">Google Drive</span>
              </div>
              <span className="text-sm text-gray-500">
                {authStatus?.google_authenticated ? 'Connected' : 'Not connected'}
              </span>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${authStatus?.folderfort_authenticated ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className="font-medium">Folderfort</span>
              </div>
              <span className="text-sm text-gray-500">
                {authStatus?.folderfort_authenticated ? 'Connected' : 'Not connected'}
              </span>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
