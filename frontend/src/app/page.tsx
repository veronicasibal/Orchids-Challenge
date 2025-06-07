'use client';

import React, { useState } from 'react';

export default function Home() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/clone-website', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadHtml = () => {
    if (!result?.cloned_html) return;
    
    const blob = new Blob([result.cloned_html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cloned-website.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Website Cloner
          </h1>
          <p className="text-lg text-gray-600">
            Enter any website URL to create an AI-powered clone
          </p>
        </div>

        {/* Input Form */}
        <div className="mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex gap-4">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter website URL (e.g., example.com)"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-lg text-black"
                disabled={loading}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSubmit(e);
                  }
                }}
              />
              <button
                onClick={handleSubmit}
                disabled={loading || !url.trim()}
                className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Cloning...
                  </div>
                ) : (
                  '🚀 Clone Website'
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="flex items-center justify-center gap-4 mb-4">
              <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-xl font-semibold text-gray-700">
                Cloning website...
              </span>
            </div>
            <p className="text-gray-600">
              This may take 30-60 seconds. We&apos;re analyzing the website and generating the clone.
            </p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">❌</span>
              <h3 className="text-lg font-semibold text-red-800">Error</h3>
            </div>
            <p className="text-red-700">{error}</p>
            <div className="mt-4 text-sm text-red-600">
              <p>Common issues:</p>
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>Make sure your backend is running (python main.py)</li>
                <li>Check if the URL is accessible</li>
                <li>Verify your Anthropic API key is set in .env file</li>
              </ul>
            </div>
          </div>
        )}

        {/* Success State */}
        {result && result.success && (
          <div className="space-y-6">
            {/* Success Message */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl">✅</span>
                <h3 className="text-lg font-semibold text-green-800">
                  Website Cloned Successfully!
                </h3>
              </div>
              <p className="text-green-700">
                Generated {result.cloned_html.length.toLocaleString()} characters of HTML
              </p>
            </div>

            {/* Actions */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex gap-4 mb-6">
                <button
                  onClick={downloadHtml}
                  className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
                >
                  Download HTML
                </button>
                <button
                  onClick={() => {
                    const newWindow = window.open();
                    if (newWindow) {
                      newWindow.document.write(result.cloned_html);
                      newWindow.document.close();
                    }
                  }}
                  className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors"
                >
                  Preview Clone
                </button>
              </div>

              {/* HTML Preview */}
              <div>
                <h4 className="text-lg font-semibold text-gray-800 mb-3">
                  Generated HTML Preview:
                </h4>
                <div className="bg-gray-100 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {result.cloned_html.substring(0, 2000)}
                    {result.cloned_html.length > 2000 && '\n... (truncated)'}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}


      </div>
    </div>
  );
}