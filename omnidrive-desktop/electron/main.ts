import { app, BrowserWindow, ipcMain, dialog, shell } from 'electron'
import { spawn } from 'child_process'
import path from 'path'

const OMNIDRIVE_CLI = path.join(process.env.HOME || '', 'Dev/omnidrive-cli')
const PYTHON_PATH = path.join(OMNIDRIVE_CLI, '.venv/bin/python3')

let mainWindow: BrowserWindow | null = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#111827',
  })

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

// CLI Runner - Execute OmniDrive commands
function runCLI(command: string, args: string[]): Promise<{ stdout: string; stderr: string; code: number }> {
  return new Promise((resolve) => {
    const proc = spawn(PYTHON_PATH, ['-m', 'omnidrive', command, ...args], {
      cwd: OMNIDRIVE_CLI,
      env: { ...process.env, PYTHONPATH: OMNIDRIVE_CLI },
    })

    let stdout = ''
    let stderr = ''

    proc.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    proc.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    proc.on('close', (code) => {
      resolve({ stdout, stderr, code: code || 0 })
    })
  })
}

// IPC Handlers
ipcMain.handle('cli:list', async (_, service: string, limit?: number) => {
  const args = ['--drive', service]
  if (limit) args.push('--limit', String(limit))
  return runCLI('list', args)
})

ipcMain.handle('cli:upload', async (_, filePath: string, service: string, parentId?: string) => {
  const args = [filePath, service]
  if (parentId) args.push('--parent-id', parentId)
  return runCLI('upload', args)
})

ipcMain.handle('cli:download', async (_, service: string, fileId: string, dest?: string) => {
  const args = [service, fileId]
  if (dest) args.push('--dest', dest)
  return runCLI('download', args)
})

ipcMain.handle('cli:delete', async (_, service: string, fileId: string, permanent?: boolean) => {
  const args = [service, fileId]
  if (permanent) args.push('--permanent')
  return runCLI('delete', args)
})

ipcMain.handle('cli:sync', async (_, source: string, target: string, dryRun?: boolean) => {
  const args = [source, target]
  if (dryRun) args.push('--dry-run')
  return runCLI('sync', args)
})

ipcMain.handle('cli:search', async (_, query: string, service?: string, topK?: number) => {
  const args = [query]
  if (service) args.push('--service', service)
  if (topK) args.push('--top-k', String(topK))
  return runCLI('search', args)
})

ipcMain.handle('cli:index', async (_, service: string, limit?: number) => {
  const args = [service]
  if (limit) args.push('--limit', String(limit))
  return runCLI('index', args)
})

ipcMain.handle('cli:workflows', async () => {
  return runCLI('workflow', ['list'])
})

ipcMain.handle('cli:runWorkflow', async (_, name: string) => {
  return runCLI('workflow', ['run', name])
})

ipcMain.handle('cli:authStatus', async () => {
  // Check auth status for both services
  const google = await runCLI('list', ['--drive', 'google', '--limit', '1'])
  const folderfort = await runCLI('list', ['--drive', 'folderfort', '--limit', '1'])
  return {
    google: google.code === 0,
    folderfort: folderfort.code === 0,
  }
})

// Native dialogs
ipcMain.handle('dialog:selectFolder', async () => {
  const result = await dialog.showOpenDialog(mainWindow!, {
    properties: ['openDirectory', 'createDirectory'],
    title: 'Select Download Location',
  })
  return result.canceled ? null : result.filePaths[0]
})

ipcMain.handle('dialog:saveFile', async (_, defaultName: string) => {
  const result = await dialog.showSaveDialog(mainWindow!, {
    defaultPath: defaultName,
    title: 'Save File As',
  })
  return result.canceled ? null : result.filePath
})

// Open file in system
ipcMain.handle('shell:openPath', async (_, filePath: string) => {
  return shell.openPath(filePath)
})

ipcMain.handle('shell:showItemInFolder', async (_, filePath: string) => {
  shell.showItemInFolder(filePath)
})
