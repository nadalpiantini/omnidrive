import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            OmniDrive
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            Multi-cloud storage management made simple
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/dashboard"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go to Dashboard
            </Link>
            <Link
              href="/dashboard/files"
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
            >
              Browse Files
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold mb-2 dark:text-white">🔐 Multi-Cloud</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Connect Google Drive, Folderfort, and more in one place
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold mb-2 dark:text-white">🔍 Smart Search</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Semantic search powered by AI to find anything instantly
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold mb-2 dark:text-white">🔄 Easy Sync</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Sync files between cloud services with one click
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
