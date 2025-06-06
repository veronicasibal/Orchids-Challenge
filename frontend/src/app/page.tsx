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
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8">
          Website Cloning Tool
        </h1>
        
        {/* Input Section */}
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <label className="block text-sm font-medium mb-2">
            Enter Website URL:
          </label>
          <div className="flex gap-4">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleCloneWebsite}
              disabled={isLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? 'Cloning...' : 'Clone Website'}
            </button>
          </div>
          {error && (
            <p className="text-red-600 mt-2">{error}</p>
          )}
        </div>

        {/* Preview Section */}
        {clonedHtml && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Cloned Website Preview:</h2>
            <div className="border border-gray-300 rounded-md overflow-hidden">
              <iframe
                srcDoc={clonedHtml}
                className="w-full h-96"
                title="Cloned Website Preview"
              />
            </div>
            <details className="mt-4">
              <summary className="cursor-pointer text-blue-600 hover:text-blue-800">
                View Generated HTML Code
              </summary>
              <pre className="bg-gray-100 p-4 rounded-md mt-2 overflow-x-auto text-sm">
                <code>{clonedHtml}</code>
              </pre>
            </details>
          </div>
        )}
      </div>
    </div>
  )
}