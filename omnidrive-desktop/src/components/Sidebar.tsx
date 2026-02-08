import { useState, useEffect } from 'react'
import {
  Cloud,
  HardDrive,
  FolderSync,
  Search,
  Workflow,
  Shield,
  Settings,
  ChevronDown,
  Check,
  Zap,
  Database,
  Sparkles,
} from 'lucide-react'

type View = 'files' | 'sync' | 'search' | 'workflows' | 'governance'

interface SidebarProps {
  currentView: View
  onViewChange: (view: View) => void
  currentService: 'google' | 'folderfort'
  onServiceChange: (service: 'google' | 'folderfort') => void
}

interface AuthStatus {
  google: boolean
  folderfort: boolean
}

export default function Sidebar({
  currentView,
  onViewChange,
  currentService,
  onServiceChange,
}: SidebarProps) {
  const [authStatus, setAuthStatus] = useState<AuthStatus>({ google: false, folderfort: false })
  const [isServiceMenuOpen, setIsServiceMenuOpen] = useState(false)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    if (typeof window.omnidrive === 'undefined') return
    try {
      const status = await window.omnidrive.authStatus()
      setAuthStatus(status)
    } catch (e) {
      console.error('Auth check failed:', e)
    }
  }

  const services = [
    {
      id: 'google' as const,
      name: 'Google Drive',
      icon: Cloud,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30',
      connected: authStatus.google,
    },
    {
      id: 'folderfort' as const,
      name: 'Folderfort',
      icon: HardDrive,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/30',
      connected: authStatus.folderfort,
    },
  ]

  const navigation = [
    { id: 'files' as View, name: 'Files', icon: Database },
    { id: 'sync' as View, name: 'Sync', icon: FolderSync },
    { id: 'search' as View, name: 'Search', icon: Search, badge: 'AI' },
    { id: 'workflows' as View, name: 'Workflows', icon: Workflow },
    { id: 'governance' as View, name: 'Governance', icon: Shield },
  ]

  const currentServiceData = services.find(s => s.id === currentService)!

  return (
    <aside className="w-64 bg-gradient-to-b from-gray-950 to-gray-900 border-r border-gray-800/50 flex flex-col">
      {/* Service Selector */}
      <div className="p-4">
        <div className="relative">
          <button
            onClick={() => setIsServiceMenuOpen(!isServiceMenuOpen)}
            className={`w-full flex items-center gap-3 p-3 rounded-xl border transition-all ${currentServiceData.bgColor} ${currentServiceData.borderColor} hover:brightness-110`}
          >
            <div className="p-2 rounded-lg bg-gray-900/50 backdrop-blur">
              <currentServiceData.icon className={`w-5 h-5 ${currentServiceData.color}`} />
            </div>
            <div className="flex-1 text-left">
              <div className="font-semibold text-sm">{currentServiceData.name}</div>
              <div className="text-xs text-gray-400 flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full ${currentServiceData.connected ? 'bg-green-400 animate-pulse' : 'bg-yellow-400'}`}></span>
                {currentServiceData.connected ? 'Connected' : 'Not connected'}
              </div>
            </div>
            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${isServiceMenuOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Dropdown */}
          {isServiceMenuOpen && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setIsServiceMenuOpen(false)} />
              <div className="absolute top-full left-0 right-0 mt-2 bg-gray-900/95 backdrop-blur-xl border border-gray-700/50 rounded-xl shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                {services.map((service) => (
                  <button
                    key={service.id}
                    onClick={() => {
                      onServiceChange(service.id)
                      setIsServiceMenuOpen(false)
                    }}
                    className={`w-full flex items-center gap-3 p-3 hover:bg-gray-800/50 transition-colors ${
                      service.id === currentService ? 'bg-gray-800/30' : ''
                    }`}
                  >
                    <service.icon className={`w-5 h-5 ${service.color}`} />
                    <div className="flex-1 text-left">
                      <div className="text-sm font-medium">{service.name}</div>
                      <div className="text-xs text-gray-500 flex items-center gap-1">
                        <span className={`w-1.5 h-1.5 rounded-full ${service.connected ? 'bg-green-400' : 'bg-yellow-400'}`}></span>
                        {service.connected ? 'Connected' : 'Not connected'}
                      </div>
                    </div>
                    {service.id === currentService && (
                      <Check className="w-4 h-4 text-primary-400" />
                    )}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-2">
        <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest px-3 mb-3">
          Navigation
        </div>
        <div className="space-y-1">
          {navigation.map((item) => (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative ${
                currentView === item.id
                  ? 'bg-gradient-to-r from-primary-500/20 to-primary-500/5 text-white shadow-lg shadow-primary-500/10'
                  : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'
              }`}
            >
              {currentView === item.id && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-primary-500 rounded-r-full" />
              )}
              <item.icon className={`w-5 h-5 transition-colors ${currentView === item.id ? 'text-primary-400' : 'text-gray-500 group-hover:text-gray-300'}`} />
              <span className="font-medium text-sm">{item.name}</span>
              {item.badge && (
                <span className="ml-auto px-1.5 py-0.5 text-[10px] font-bold bg-gradient-to-r from-purple-500 to-pink-500 rounded-md">
                  {item.badge}
                </span>
              )}
            </button>
          ))}
        </div>
      </nav>

      {/* Storage Info */}
      <div className="p-4">
        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur rounded-xl p-4 border border-gray-700/30">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-300">Storage</span>
            <Sparkles className="w-4 h-4 text-primary-400" />
          </div>
          <div className="h-2 bg-gray-700/50 rounded-full overflow-hidden mb-2">
            <div
              className="h-full bg-gradient-to-r from-primary-500 via-blue-500 to-cyan-500 rounded-full transition-all duration-1000"
              style={{ width: '45%' }}
            />
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400">6.8 GB used</span>
            <span className="text-gray-500">of 15 GB</span>
          </div>
        </div>
      </div>

      {/* Settings */}
      <div className="p-3 border-t border-gray-800/50">
        <button className="w-full flex items-center gap-3 px-3 py-2.5 text-gray-400 hover:text-white hover:bg-gray-800/50 rounded-xl transition-all text-sm group">
          <Settings className="w-5 h-5 text-gray-500 group-hover:text-gray-300 group-hover:rotate-90 transition-all duration-300" />
          <span className="font-medium">Settings</span>
        </button>
      </div>

      {/* Version */}
      <div className="px-4 pb-4">
        <div className="flex items-center gap-2 text-[10px] text-gray-600">
          <Zap className="w-3 h-3" />
          <span>OmniDrive Desktop v1.0.0</span>
        </div>
      </div>
    </aside>
  )
}
