import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
  ArrowRightLeft,
  CheckCircle,
  AlertCircle,
  Loader2,
  Cloud,
  HardDrive,
  FolderSync,
  Sparkles,
  Eye,
  Zap,
  Clock,
  FileText,
  ArrowRight,
} from 'lucide-react'

interface SyncJob {
  id: string
  source: string
  target: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  filesProcessed?: number
  totalFiles?: number
  error?: string
}

const services = {
  google: { name: 'Google Drive', icon: Cloud, color: 'blue', gradient: 'from-blue-500/20 to-blue-600/10' },
  folderfort: { name: 'Folderfort', icon: HardDrive, color: 'emerald', gradient: 'from-emerald-500/20 to-emerald-600/10' },
}

export default function SyncPanel() {
  const [source, setSource] = useState<'google' | 'folderfort'>('google')
  const [target, setTarget] = useState<'google' | 'folderfort'>('folderfort')
  const [dryRun, setDryRun] = useState(true)
  const [syncHistory, setSyncHistory] = useState<SyncJob[]>([])

  const syncMutation = useMutation({
    mutationFn: async () => {
      if (typeof window.omnidrive === 'undefined') {
        await new Promise(r => setTimeout(r, 2000))
        return { code: 0, stdout: 'Sync completed: 10 files synced', stderr: '' }
      }
      return window.omnidrive.sync(source, target, dryRun)
    },
    onSuccess: (result) => {
      const newJob: SyncJob = {
        id: Date.now().toString(),
        source,
        target,
        status: result.code === 0 ? 'completed' : 'failed',
        filesProcessed: 10,
        totalFiles: 10,
        error: result.code !== 0 ? result.stderr : undefined,
      }
      setSyncHistory(prev => [newJob, ...prev])
    },
  })

  const swapServices = () => {
    const temp = source
    setSource(target)
    setTarget(temp)
  }

  const sourceService = services[source]
  const targetService = services[target]

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="p-3 bg-gradient-to-br from-primary-500/20 to-purple-500/20 rounded-xl">
          <FolderSync className="w-7 h-7 text-primary-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold">Cloud Sync</h2>
          <p className="text-gray-400 text-sm">Synchronize files between your cloud services</p>
        </div>
      </div>

      {/* Sync Configuration Card */}
      <div className="relative overflow-hidden bg-gradient-to-br from-gray-800/80 to-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-8 mb-6">
        {/* Background decoration */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-primary-500/10 to-purple-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />

        <div className="relative">
          {/* Service Selection */}
          <div className="flex items-center justify-center gap-6 mb-8">
            {/* Source */}
            <div className="flex-1">
              <label className="text-xs text-gray-500 uppercase tracking-widest mb-3 block font-medium">
                Source
              </label>
              <div className={`relative p-4 bg-gradient-to-br ${sourceService.gradient} rounded-xl border border-${sourceService.color}-500/30`}>
                <select
                  value={source}
                  onChange={(e) => setSource(e.target.value as 'google' | 'folderfort')}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                >
                  <option value="google">Google Drive</option>
                  <option value="folderfort">Folderfort</option>
                </select>
                <div className="flex items-center gap-3 pointer-events-none">
                  <sourceService.icon className={`w-8 h-8 text-${sourceService.color}-400`} />
                  <div>
                    <div className="font-semibold">{sourceService.name}</div>
                    <div className="text-xs text-gray-500">Click to change</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Swap Button */}
            <button
              onClick={swapServices}
              className="mt-6 p-4 bg-gray-700/50 hover:bg-gray-600/50 rounded-xl transition-all hover:scale-110 group"
            >
              <ArrowRightLeft className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" />
            </button>

            {/* Target */}
            <div className="flex-1">
              <label className="text-xs text-gray-500 uppercase tracking-widest mb-3 block font-medium">
                Target
              </label>
              <div className={`relative p-4 bg-gradient-to-br ${targetService.gradient} rounded-xl border border-${targetService.color}-500/30`}>
                <select
                  value={target}
                  onChange={(e) => setTarget(e.target.value as 'google' | 'folderfort')}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                >
                  <option value="google">Google Drive</option>
                  <option value="folderfort">Folderfort</option>
                </select>
                <div className="flex items-center gap-3 pointer-events-none">
                  <targetService.icon className={`w-8 h-8 text-${targetService.color}-400`} />
                  <div>
                    <div className="font-semibold">{targetService.name}</div>
                    <div className="text-xs text-gray-500">Click to change</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Visual Flow Arrow */}
          <div className="flex items-center justify-center mb-8">
            <div className="flex items-center gap-2 px-4 py-2 bg-gray-800/50 rounded-full">
              <FileText className="w-4 h-4 text-gray-500" />
              <ArrowRight className="w-4 h-4 text-primary-400 animate-pulse" />
              <FileText className="w-4 h-4 text-gray-500" />
            </div>
          </div>

          {/* Options Row */}
          <div className="flex items-center gap-4 mb-8">
            {/* Dry Run Toggle */}
            <div className="flex-1 flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-700/50">
              <div className="flex items-center gap-3">
                <Eye className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="text-sm font-medium">Preview Mode</div>
                  <div className="text-xs text-gray-500">See changes before syncing</div>
                </div>
              </div>
              <button
                onClick={() => setDryRun(!dryRun)}
                className={`relative w-14 h-7 rounded-full transition-all ${
                  dryRun ? 'bg-gradient-to-r from-primary-500 to-primary-600' : 'bg-gray-600'
                }`}
              >
                <div
                  className={`absolute top-1 w-5 h-5 bg-white rounded-full shadow-lg transition-all ${
                    dryRun ? 'left-8' : 'left-1'
                  }`}
                />
              </button>
            </div>

            {/* Smart Sync Badge */}
            <div className="flex items-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-xl border border-purple-500/20">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span className="text-sm text-purple-300">Smart Sync</span>
            </div>
          </div>

          {/* Sync Button */}
          <button
            onClick={() => syncMutation.mutate()}
            disabled={syncMutation.isPending || source === target}
            className="relative w-full group"
          >
            {/* Glow effect */}
            <div className={`absolute -inset-1 bg-gradient-to-r from-primary-500 to-purple-500 rounded-xl blur opacity-0 transition-opacity ${
              !syncMutation.isPending && source !== target ? 'group-hover:opacity-50' : ''
            }`} />

            <div className={`relative flex items-center justify-center gap-3 py-4 rounded-xl font-semibold text-lg transition-all ${
              syncMutation.isPending || source === target
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-500 hover:to-primary-600 text-white'
            }`}>
              {syncMutation.isPending ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin" />
                  <span>Syncing...</span>
                </>
              ) : (
                <>
                  {dryRun ? <Eye className="w-6 h-6" /> : <Zap className="w-6 h-6" />}
                  <span>{dryRun ? 'Preview Sync' : 'Start Sync'}</span>
                </>
              )}
            </div>
          </button>

          {source === target && (
            <p className="text-center text-sm text-yellow-400 mt-3 flex items-center justify-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Source and target must be different
            </p>
          )}
        </div>
      </div>

      {/* Sync History */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Clock className="w-5 h-5 text-gray-500" />
            Sync History
          </h3>
          {syncHistory.length > 0 && (
            <button
              onClick={() => setSyncHistory([])}
              className="text-xs text-gray-500 hover:text-white transition-colors"
            >
              Clear
            </button>
          )}
        </div>

        {syncHistory.length === 0 ? (
          <div className="text-center py-12 bg-gray-800/30 rounded-xl border border-gray-800/50 border-dashed">
            <FolderSync className="w-12 h-12 text-gray-700 mx-auto mb-3" />
            <p className="text-gray-500">No sync jobs yet</p>
            <p className="text-sm text-gray-600 mt-1">Start a sync to see history here</p>
          </div>
        ) : (
          <div className="space-y-3">
            {syncHistory.map((job) => {
              const jobSource = services[job.source as keyof typeof services]
              const jobTarget = services[job.target as keyof typeof services]

              return (
                <div
                  key={job.id}
                  className={`flex items-center justify-between p-4 rounded-xl border transition-all ${
                    job.status === 'completed'
                      ? 'bg-green-500/5 border-green-500/20'
                      : job.status === 'failed'
                      ? 'bg-red-500/5 border-red-500/20'
                      : 'bg-gray-800/50 border-gray-700/50'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    {job.status === 'completed' ? (
                      <div className="p-2 bg-green-500/10 rounded-lg">
                        <CheckCircle className="w-5 h-5 text-green-400" />
                      </div>
                    ) : job.status === 'failed' ? (
                      <div className="p-2 bg-red-500/10 rounded-lg">
                        <AlertCircle className="w-5 h-5 text-red-400" />
                      </div>
                    ) : (
                      <div className="p-2 bg-primary-500/10 rounded-lg">
                        <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />
                      </div>
                    )}
                    <div>
                      <div className="flex items-center gap-2 text-sm font-medium">
                        <jobSource.icon className={`w-4 h-4 text-${jobSource.color}-400`} />
                        <span>{jobSource.name}</span>
                        <ArrowRight className="w-3 h-3 text-gray-600" />
                        <jobTarget.icon className={`w-4 h-4 text-${jobTarget.color}-400`} />
                        <span>{jobTarget.name}</span>
                      </div>
                      {job.error ? (
                        <div className="text-xs text-red-400 mt-1">{job.error}</div>
                      ) : job.filesProcessed ? (
                        <div className="text-xs text-gray-500 mt-1">
                          {job.filesProcessed} files processed
                        </div>
                      ) : null}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(parseInt(job.id)).toLocaleTimeString()}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
