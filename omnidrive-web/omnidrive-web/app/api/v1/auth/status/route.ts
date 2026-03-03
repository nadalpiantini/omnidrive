import { NextResponse } from 'next/server'
import { supabaseAdmin } from '@/lib/supabase'

export async function GET() {
  try {
    // Check auth configs in database
    const { data: configs, error } = await supabaseAdmin
      .from('omnidrive_auth_configs')
      .select('service, is_active')

    if (error) {
      console.error('Error fetching auth configs:', error)
    }

    const googleConfig = configs?.find(c => c.service === 'google')
    const folderfortConfig = configs?.find(c => c.service === 'folderfort')

    return NextResponse.json({
      google_authenticated: googleConfig?.is_active ?? false,
      folderfort_authenticated: folderfortConfig?.is_active ?? false,
      google_email: process.env.GOOGLE_SERVICE_EMAIL || null,
      folderfort_email: process.env.FOLDERFORT_EMAIL || null
    })
  } catch (error) {
    console.error('Auth status error:', error)
    return NextResponse.json({
      google_authenticated: false,
      folderfort_authenticated: false
    })
  }
}
