import { NextRequest, NextResponse } from 'next/server'
import { supabaseAdmin } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const service = searchParams.get('service') || 'google'
    const folderId = searchParams.get('folder_id')
    const limit = parseInt(searchParams.get('limit') || '100')

    // Query files from database
    let query = supabaseAdmin
      .from('omnidrive_files')
      .select('*')
      .eq('service', service)
      .order('modified_at', { ascending: false })
      .limit(limit)

    if (folderId) {
      query = query.eq('parent_id', folderId)
    }

    const { data: files, error, count } = await query

    if (error) {
      console.error('Error fetching files:', error)
      return NextResponse.json({ error: 'Failed to fetch files' }, { status: 500 })
    }

    // Transform to API format
    const transformedFiles = (files || []).map(file => ({
      id: file.file_id,
      name: file.name,
      size: file.size,
      mime_type: file.mime_type,
      created_time: file.created_at,
      modified_time: file.modified_at,
      parent_id: file.parent_id,
      service: file.service
    }))

    return NextResponse.json({
      files: transformedFiles,
      total: count || transformedFiles.length,
      service
    })
  } catch (error) {
    console.error('Files API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
