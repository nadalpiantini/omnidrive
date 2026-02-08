import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  CheckCircle,
  XCircle,
  Loader2,
  Shield,
  Activity,
  Cloud,
  HardDrive,
  Wifi,
  WifiOff,
  Zap,
  Clock,
} from 'lucide-react'

export default function StatusBar() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000)
    return () => clearInterval(timer)
  }, [])

  // Monitor online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const { data: authStatus, isLoading, dataUpdatedAt } = useQuery({
    queryKey: ['authStatus'],
    queryFn: async () => {
      if (typeof window.omnidrive === 'undefined') {
        return { google: true, folderfort: true }
      }
      return window.omnidrive.authStatus()
    },
    refetchInterval: 60000,
  })

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getLastChecked = () => {
    if (!dataUpdatedAt) return 'Never'
    const diff = Date.now() - dataUpdatedAt
    if (diff < 60000) return 'Just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    return `${Math.floor(diff / 3600000)}h ago`
  }

  const connectedCount = (authStatus?.google ? 1 : 0) + (authStatus?.folderfort ? 1 : 0)

  return (
    <footer className="h-9 bg-gradient-to-r from-gray-950 via-gray-900 to-gray-950 border-t border-gray-800/50 flex items-center justify-between px-4 text-xs backdrop-blur-sm">
      {/* Left side - Connection status */}
      <div className="flex items-center gap-3">
        {/* Network indicator */}
        <div className={`flex items-center gap-1.5 px-2 py-1 rounded-md ${
          isOnline
            ? 'bg-green-500/10 text-green-400'
            : 'bg-red-500/10 text-red-400'
        }`}>
          {isOnline ? (
            <Wifi className="w-3 h-3" />
          ) : (
            <WifiOff className="w-3 h-3" />
          )}
          <span className="font-medium">{isOnline ? 'Online' : 'Offline'}</span>
        </div>

        <div className="w-px h-4 bg-gray-800" />

        {/* Service connections */}
        {isLoading ? (
          <div className="flex items-center gap-1.5 text-gray-500">
            <Loader2 className="w-3 h-3 animate-spin" />
            <span>Checking...</span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            {/* Google Drive */}
            <div
              className={`group flex items-center gap-1.5 px-2 py-1 rounded-md transition-all cursor-default ${
                authStatus?.google
                  ? 'bg-blue-500/10 hover:bg-blue-500/20'
                  : 'bg-gray-800/50 hover:bg-gray-700/50'
              }`}
              title={authStatus?.google ? 'Google Drive connected' : 'Google Drive disconnected'}
            >
              <Cloud className={`w-3 h-3 ${authStatus?.google ? 'text-blue-400' : 'text-gray-600'}`} />
              <span className={authStatus?.google ? 'text-blue-300' : 'text-gray-600'}>
                Google
              </span>
              {authStatus?.google ? (
                <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              ) : (
                <XCircle className="w-3 h-3 text-red-400 opacity-0 group-hover:opacity-100 transition-opacity" />
              )}
            </div>

            {/* Folderfort */}
            <div
              className={`group flex items-center gap-1.5 px-2 py-1 rounded-md transition-all cursor-default ${
                authStatus?.folderfort
                  ? 'bg-emerald-500/10 hover:bg-emerald-500/20'
                  : 'bg-gray-800/50 hover:bg-gray-700/50'
              }`}
              title={authStatus?.folderfort ? 'Folderfort connected' : 'Folderfort disconnected'}
            >
              <HardDrive className={`w-3 h-3 ${authStatus?.folderfort ? 'text-emerald-400' : 'text-gray-600'}`} />
              <span className={authStatus?.folderfort ? 'text-emerald-300' : 'text-gray-600'}>
                Folderfort
              </span>
              {authStatus?.folderfort ? (
                <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              ) : (
                <XCircle className="w-3 h-3 text-red-400 opacity-0 group-hover:opacity-100 transition-opacity" />
              )}
            </div>
          </div>
        )}
      </div>

      {/* Center - Activity pulse */}
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1.5 px-2 py-1 bg-gray-800/30 rounded-md">
          <Activity className="w-3 h-3 text-primary-400" />
          <span className="text-gray-400">
            {connectedCount}/2 services
          </span>
        </div>
      </div>

      {/* Right side - System status */}
      <div className="flex items-center gap-3">
        {/* Governance */}
        <div className="flex items-center gap-1.5 px-2 py-1 bg-purple-500/10 rounded-md">
          <Shield className="w-3 h-3 text-purple-400" />
          <span className="text-purple-300">Governance</span>
          <CheckCircle className="w-3 h-3 text-green-400" />
        </div>

        <div className="w-px h-4 bg-gray-800" />

        {/* Last checked */}
        <div
          className="flex items-center gap-1.5 text-gray-500 cursor-default"
          title={`Last status check: ${getLastChecked()}`}
        >
          <Zap className="w-3 h-3" />
          <span>{getLastChecked()}</span>
        </div>

        <div className="w-px h-4 bg-gray-800" />

        {/* Time */}
        <div className="flex items-center gap-1.5 text-gray-400">
          <Clock className="w-3 h-3" />
          <span className="font-mono">{formatTime(currentTime)}</span>
        </div>
      </div>
    </footer>
  )
}
