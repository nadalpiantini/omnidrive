import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import {
  Sparkles,
  Workflow,
  Shield,
  Brain,
  GitBranch,
  FileCheck,
  AlertTriangle,
  Lock,
  Activity,
} from 'lucide-react'
import Sidebar from './components/Sidebar'
import FileBrowser from './components/FileBrowser'
import SyncPanel from './components/SyncPanel'
import SearchBar from './components/SearchBar'
import StatusBar from './components/StatusBar'

const queryClient = new QueryClient()

type View = 'files' | 'sync' | 'search' | 'workflows' | 'governance'

// Placeholder components with modern UI
function SearchView() {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center px-8">
      <div className="relative mb-6">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/30 to-pink-500/30 rounded-full blur-2xl" />
        <div className="relative p-6 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-2xl border border-purple-500/30">
          <Brain className="w-16 h-16 text-purple-400" />
        </div>
      </div>
      <h2 className="text-2xl font-bold mb-3 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
        AI-Powered Search
      </h2>
      <p className="text-gray-400 max-w-md mb-6">
        Search across all your files using natural language. Our RAG system understands context and semantic meaning.
      </p>
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Sparkles className="w-4 h-4 text-purple-400" />
        <span>Powered by embeddings + vector search</span>
      </div>
    </div>
  )
}

function WorkflowsView() {
  const workflows = [
    { id: 1, name: 'Smart Backup', description: 'Automated backup to multiple clouds', icon: GitBranch, status: 'active' },
    { id: 2, name: 'Sync Watch', description: 'Real-time folder synchronization', icon: Activity, status: 'paused' },
    { id: 3, name: 'File Cleanup', description: 'Remove duplicates and old files', icon: FileCheck, status: 'inactive' },
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold mb-2">Workflows</h2>
          <p className="text-gray-400">Automate your file operations with intelligent workflows</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg font-medium transition-colors">
          <Workflow className="w-4 h-4" />
          New Workflow
        </button>
      </div>

      <div className="grid gap-4">
        {workflows.map((workflow) => (
          <div
            key={workflow.id}
            className="group p-5 bg-gradient-to-r from-gray-800/50 to-gray-800/30 rounded-xl border border-gray-700/50 hover:border-gray-600 transition-all cursor-pointer"
          >
            <div className="flex items-start gap-4">
              <div className="p-3 bg-gray-700/50 rounded-xl group-hover:bg-gray-700 transition-colors">
                <workflow.icon className="w-6 h-6 text-primary-400" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="font-semibold text-white">{workflow.name}</h3>
                  <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                    workflow.status === 'active' ? 'bg-green-500/20 text-green-400' :
                    workflow.status === 'paused' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {workflow.status}
                  </span>
                </div>
                <p className="text-sm text-gray-400">{workflow.description}</p>
              </div>
              <button className="opacity-0 group-hover:opacity-100 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition-all">
                Configure
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 p-6 bg-gradient-to-br from-primary-500/10 to-purple-500/10 rounded-xl border border-primary-500/20">
        <div className="flex items-start gap-4">
          <Sparkles className="w-6 h-6 text-primary-400 shrink-0" />
          <div>
            <h4 className="font-semibold mb-1">LangGraph Powered</h4>
            <p className="text-sm text-gray-400">
              Our workflows use LangGraph agents for intelligent decision-making, error recovery, and adaptive execution.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function GovernanceView() {
  const policies = [
    { name: 'Deletion Approval', description: 'Require confirmation before permanent deletes', enabled: true, level: 'critical' },
    { name: 'Sync Audit Log', description: 'Log all sync operations for compliance', enabled: true, level: 'normal' },
    { name: 'Large File Warning', description: 'Alert before uploading files > 100MB', enabled: false, level: 'warning' },
    { name: 'External Share Block', description: 'Prevent sharing outside organization', enabled: true, level: 'critical' },
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold mb-2">Governance</h2>
          <p className="text-gray-400">Control access, policies, and audit trails</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded-lg">
          <Shield className="w-4 h-4 text-green-400" />
          <span className="text-sm text-green-400 font-medium">All policies active</span>
        </div>
      </div>

      <div className="grid gap-4 mb-8">
        {policies.map((policy, i) => (
          <div
            key={i}
            className={`p-5 rounded-xl border transition-all ${
              policy.enabled
                ? 'bg-gray-800/50 border-gray-700/50'
                : 'bg-gray-900/50 border-gray-800/50 opacity-60'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-start gap-4">
                <div className={`p-2 rounded-lg ${
                  policy.level === 'critical' ? 'bg-red-500/10' :
                  policy.level === 'warning' ? 'bg-yellow-500/10' :
                  'bg-gray-700/50'
                }`}>
                  {policy.level === 'critical' ? (
                    <Lock className={`w-5 h-5 ${policy.enabled ? 'text-red-400' : 'text-gray-600'}`} />
                  ) : policy.level === 'warning' ? (
                    <AlertTriangle className={`w-5 h-5 ${policy.enabled ? 'text-yellow-400' : 'text-gray-600'}`} />
                  ) : (
                    <Shield className={`w-5 h-5 ${policy.enabled ? 'text-primary-400' : 'text-gray-600'}`} />
                  )}
                </div>
                <div>
                  <h3 className="font-medium text-white">{policy.name}</h3>
                  <p className="text-sm text-gray-400 mt-0.5">{policy.description}</p>
                </div>
              </div>
              <button
                className={`relative w-12 h-6 rounded-full transition-colors ${
                  policy.enabled ? 'bg-green-600' : 'bg-gray-600'
                }`}
              >
                <div
                  className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                    policy.enabled ? 'left-7' : 'left-1'
                  }`}
                />
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="p-6 bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl border border-gray-700/30">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-primary-400" />
          Recent Audit Log
        </h3>
        <div className="space-y-3 text-sm">
          <div className="flex items-center gap-3 text-gray-400">
            <span className="w-20 text-xs text-gray-600">2 min ago</span>
            <span className="px-2 py-0.5 text-xs bg-green-500/20 text-green-400 rounded">SYNC</span>
            <span>12 files synced from Google Drive to Folderfort</span>
          </div>
          <div className="flex items-center gap-3 text-gray-400">
            <span className="w-20 text-xs text-gray-600">15 min ago</span>
            <span className="px-2 py-0.5 text-xs bg-yellow-500/20 text-yellow-400 rounded">DELETE</span>
            <span>contract_old.pdf moved to trash (approval granted)</span>
          </div>
          <div className="flex items-center gap-3 text-gray-400">
            <span className="w-20 text-xs text-gray-600">1 hour ago</span>
            <span className="px-2 py-0.5 text-xs bg-blue-500/20 text-blue-400 rounded">UPLOAD</span>
            <span>5 files uploaded to Google Drive</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [currentView, setCurrentView] = useState<View>('files')
  const [currentService, setCurrentService] = useState<'google' | 'folderfort'>('google')

  return (
    <QueryClientProvider client={queryClient}>
      <div className="h-screen flex flex-col bg-gray-900 text-white">
        {/* Title Bar */}
        <div className="drag-region h-9 bg-gradient-to-r from-gray-950 via-gray-900 to-gray-950 border-b border-gray-800/50 flex items-center justify-center">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gradient-to-br from-primary-400 to-purple-500" />
            <span className="text-xs text-gray-400 font-medium tracking-wide">OmniDrive Desktop</span>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          <Sidebar
            currentView={currentView}
            onViewChange={setCurrentView}
            currentService={currentService}
            onServiceChange={setCurrentService}
          />

          {/* Content Area */}
          <main className="flex-1 flex flex-col overflow-hidden bg-gradient-to-br from-gray-900 via-gray-900 to-gray-950">
            {/* Search Bar - only show on files view */}
            {currentView === 'files' && (
              <div className="p-4 border-b border-gray-800/50">
                <SearchBar />
              </div>
            )}

            {/* Dynamic Content */}
            <div className="flex-1 overflow-auto p-6">
              {currentView === 'files' && (
                <FileBrowser service={currentService} />
              )}
              {currentView === 'sync' && (
                <SyncPanel />
              )}
              {currentView === 'search' && (
                <SearchView />
              )}
              {currentView === 'workflows' && (
                <WorkflowsView />
              )}
              {currentView === 'governance' && (
                <GovernanceView />
              )}
            </div>
          </main>
        </div>

        {/* Status Bar */}
        <StatusBar />
      </div>
    </QueryClientProvider>
  )
}
