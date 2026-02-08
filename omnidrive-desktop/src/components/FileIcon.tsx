import {
  File,
  FileText,
  FileSpreadsheet,
  FileImage,
  FileVideo,
  FileAudio,
  FileCode,
  FileArchive,
  Presentation,
  Folder,
} from 'lucide-react'

interface FileIconProps {
  mimeType?: string
  name: string
  isFolder?: boolean
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizeClasses = {
  sm: 'w-5 h-5',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
}

export default function FileIcon({ mimeType, name, isFolder, size = 'md', className = '' }: FileIconProps) {
  const sizeClass = sizeClasses[size]

  if (isFolder) {
    return <Folder className={`${sizeClass} text-yellow-400 ${className}`} />
  }

  // Determine icon by mime type or extension
  const ext = name.split('.').pop()?.toLowerCase() || ''

  // Google Workspace files
  if (mimeType?.includes('google-apps.document') || mimeType?.includes('google-apps.spreadsheet') || mimeType?.includes('google-apps.presentation')) {
    if (mimeType.includes('spreadsheet')) {
      return <FileSpreadsheet className={`${sizeClass} text-green-400 ${className}`} />
    }
    if (mimeType.includes('presentation')) {
      return <Presentation className={`${sizeClass} text-orange-400 ${className}`} />
    }
    return <FileText className={`${sizeClass} text-blue-400 ${className}`} />
  }

  // By extension
  const iconMap: Record<string, { icon: typeof File; color: string }> = {
    // Documents
    pdf: { icon: FileText, color: 'text-red-400' },
    doc: { icon: FileText, color: 'text-blue-400' },
    docx: { icon: FileText, color: 'text-blue-400' },
    txt: { icon: FileText, color: 'text-gray-400' },
    md: { icon: FileText, color: 'text-gray-400' },
    rtf: { icon: FileText, color: 'text-blue-300' },

    // Spreadsheets
    xls: { icon: FileSpreadsheet, color: 'text-green-400' },
    xlsx: { icon: FileSpreadsheet, color: 'text-green-400' },
    csv: { icon: FileSpreadsheet, color: 'text-green-300' },

    // Presentations
    ppt: { icon: Presentation, color: 'text-orange-400' },
    pptx: { icon: Presentation, color: 'text-orange-400' },

    // Images
    jpg: { icon: FileImage, color: 'text-purple-400' },
    jpeg: { icon: FileImage, color: 'text-purple-400' },
    png: { icon: FileImage, color: 'text-purple-400' },
    gif: { icon: FileImage, color: 'text-purple-400' },
    svg: { icon: FileImage, color: 'text-purple-400' },
    webp: { icon: FileImage, color: 'text-purple-400' },

    // Video
    mp4: { icon: FileVideo, color: 'text-pink-400' },
    mov: { icon: FileVideo, color: 'text-pink-400' },
    avi: { icon: FileVideo, color: 'text-pink-400' },
    mkv: { icon: FileVideo, color: 'text-pink-400' },
    webm: { icon: FileVideo, color: 'text-pink-400' },

    // Audio
    mp3: { icon: FileAudio, color: 'text-cyan-400' },
    wav: { icon: FileAudio, color: 'text-cyan-400' },
    flac: { icon: FileAudio, color: 'text-cyan-400' },
    m4a: { icon: FileAudio, color: 'text-cyan-400' },

    // Code
    js: { icon: FileCode, color: 'text-yellow-400' },
    ts: { icon: FileCode, color: 'text-blue-400' },
    py: { icon: FileCode, color: 'text-green-400' },
    html: { icon: FileCode, color: 'text-orange-400' },
    css: { icon: FileCode, color: 'text-blue-300' },
    json: { icon: FileCode, color: 'text-yellow-300' },

    // Archives
    zip: { icon: FileArchive, color: 'text-amber-400' },
    rar: { icon: FileArchive, color: 'text-amber-400' },
    '7z': { icon: FileArchive, color: 'text-amber-400' },
    tar: { icon: FileArchive, color: 'text-amber-400' },
    gz: { icon: FileArchive, color: 'text-amber-400' },
  }

  const config = iconMap[ext]
  if (config) {
    const Icon = config.icon
    return <Icon className={`${sizeClass} ${config.color} ${className}`} />
  }

  // Default
  return <File className={`${sizeClass} text-gray-400 ${className}`} />
}
