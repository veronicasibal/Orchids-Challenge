'use client'

import { useState } from 'react'

export default function Home() {
  const [url, setUrl] = useState('')
  const [clonedHtml, setClonedHtml] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleCloneWebsite = async () => {
    if (!url) {
      setError('Please enter a URL')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await fetch('http://localhost:8000/clone-website', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url })
      })

      const data = await response.json()

      if (response.ok) {
        setClonedHtml(data.cloned_html)
      } else {
        setError(data.error || 'Failed to clone website')
      }
    } catch (err) {
      setError('Network error - make sure your backend is running')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-black to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200/50 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              🚀 Website Cloning Tool
            </h1>
            <p className="mt-2 text-gray-600">
              Enter any website URL and watch AI recreate it instantly
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Input Section */}
        <div className="bg-white/70 backdrop-blur-sm p-8 rounded-2xl shadow-xl border border-gray-200/50 mb-8">
          <div className="max-w-4xl mx-auto">
            <label className="block text-lg font-semibold text-gray-700 mb-4">
              🌐 Enter Website URL
            </label>
            
            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com"
                  className="w-full px-6 py-4 text-lg border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/80"
                  disabled={isLoading}
                />
              </div>
              
              <button
                onClick={handleCloneWebsite}
                disabled={isLoading || !url.trim()}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                    Cloning...
                  </>
                ) : (
                  <>
                    ✨ Clone Website
                  </>
                )}
              </button>
            </div>

            {/* Error Display */}
            {error && (
              <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg">
                <div className="flex items-center">
                  <span className="text-red-500 mr-2">⚠️</span>
                  <p className="text-red-700 font-medium">{error}</p>
                </div>
              </div>
            )}

            {/* Success Message */}
            {clonedHtml && !isLoading && (
              <div className="mt-4 p-4 bg-green-50 border-l-4 border-green-500 rounded-lg">
                <div className="flex items-center">
                  <span className="text-green-500 mr-2">✅</span>
                  <p className="text-green-700 font-medium">Website cloned successfully!</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Preview Section */}
        {clonedHtml && (
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 overflow-hidden">
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-8 py-6 border-b border-gray-200/50">
              <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-3">
                🎨 Cloned Website Preview
              </h2>
              <p className="text-gray-600 mt-1">
                Your website has been successfully recreated using AI
              </p>
            </div>
            
            <div className="p-8">
              {/* Preview Frame */}
              <div className="relative">
                <div className="absolute -inset-4 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl blur-xl"></div>
                <div className="relative bg-white rounded-xl border-2 border-gray-200 overflow-hidden shadow-2xl">
                  {/* Browser Mock Header */}
                  <div className="bg-gray-100 px-4 py-3 border-b border-gray-200 flex items-center gap-2">
                    <div className="flex gap-2">
                      <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                      <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                      <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                    </div>
                    <div className="flex-1 mx-4">
                      <div className="bg-white rounded-md px-3 py-1 text-sm text-gray-500 border">
                        🌐 {url}
                      </div>
                    </div>
                  </div>
                  
                  {/* Website Preview */}
                  <iframe
                    srcDoc={clonedHtml}
                    className="w-full h-96 border-0"
                    title="Cloned Website Preview"
                  />
                </div>
              </div>

              {/* Code View */}
              <details className="mt-8">
                <summary className="cursor-pointer text-blue-600 hover:text-blue-800 font-semibold text-lg flex items-center gap-2 py-2">
                  📄 View Generated HTML Code
                  <span className="text-sm text-gray-500 font-normal">(Click to expand)</span>
                </summary>
                <div className="mt-4 relative">
                  <div className="absolute top-4 right-4 z-10">
                    <button
                      onClick={() => navigator.clipboard.writeText(clonedHtml)}
                      className="px-3 py-1 bg-gray-800 text-white text-sm rounded-md hover:bg-gray-700 transition-colors"
                    >
                      📋 Copy
                    </button>
                  </div>
                  <pre className="bg-gray-900 text-green-400 p-6 rounded-xl overflow-x-auto text-sm border-2 border-gray-700 font-mono leading-relaxed">
                    <code>{clonedHtml}</code>
                  </pre>
                </div>
              </details>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-12">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mb-6">
                <div className="animate-spin rounded-full h-8 w-8 border-3 border-white border-t-transparent"></div>
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                🤖 AI is working its magic...
              </h3>
              <p className="text-gray-600">
                Analyzing the website and generating a beautiful clone
              </p>
              <div className="mt-6 bg-gray-200 rounded-full h-2 overflow-hidden">
                <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse"></div>
              </div>
            </div>
          </div>
        )}

        {/* Info Cards */}
        {!clonedHtml && !isLoading && (
          <div className="grid md:grid-cols-3 gap-6 mt-8">
            <div className="bg-white/50 backdrop-blur-sm p-6 rounded-xl border border-gray-200/50">
              <div className="text-2xl mb-3">🎯</div>
              <h3 className="font-semibold text-gray-800 mb-2">Smart Analysis</h3>
              <p className="text-gray-600 text-sm">
                AI analyzes the website's structure, design, and content
              </p>
            </div>
            
            <div className="bg-white/50 backdrop-blur-sm p-6 rounded-xl border border-gray-200/50">
              <div className="text-2xl mb-3">⚡</div>
              <h3 className="font-semibold text-gray-800 mb-2">Lightning Fast</h3>
              <p className="text-gray-600 text-sm">
                Get results in seconds with modern web scraping technology
              </p>
            </div>
            
            <div className="bg-white/50 backdrop-blur-sm p-6 rounded-xl border border-gray-200/50">
              <div className="text-2xl mb-3">🎨</div>
              <h3 className="font-semibold text-gray-800 mb-2">Perfect Recreation</h3>
              <p className="text-gray-600 text-sm">
                Claude AI recreates websites with modern, responsive design
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="mt-16 bg-white/30 backdrop-blur-sm border-t border-gray-200/50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center text-gray-600">
            <p className="mb-2">
              🚀 Powered by <span className="font-semibold">Claude AI</span> and <span className="font-semibold">Next.js</span>
            </p>
            <p className="text-sm">
              Built for the Orchids SWE Internship Challenge
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}