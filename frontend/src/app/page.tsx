'use client' //tells Next.js the page needs to be interactive (NOT static)
import { useState } from 'react' //import useState from React, which remembers and updates information about the website cloning (url info, etc)

export default function Home() { //main components of webpage for next.js to use
  const [url, setUrl] = useState('') //remembers what website url the user typed
  const [clonedHtml, setClonedHtml] = useState('') //remembers the new websites HTML code that was cloned
  const [isLoading, setIsLoading] = useState(false) //remembers if we're currently working on cloning or not (provides loading status for user)
  const [error, setError] = useState('') //remembers any error message

  const handleCloneWebsite = async () => { //function for what happens when the user clicks clone website
    if (!url) { //if user didn't type but pressed button
      setError('Please enter a URL') //error 
      return //stop here
    }

    setIsLoading(true) //button will now show cloning status
    setError('') //forget any old error messages
    
    try {
      const response = await fetch('http://localhost:8000/clone-website', { //try catch statement
        method: 'POST', //sending to backend server
        headers: {
          'Content-Type': 'application/json', //json format data
        },
        body: JSON.stringify({ url }) //actual url data being sent
      })
      
      const data = await response.json() //stores data 
      
      if (response.ok) { //checks if backend works
        setClonedHtml(data.cloned_html) //sets cloned html code
      } else {
        setError(data.error || 'Failed to clone website') //throws error message
      }
    } catch (err) { //if any error in try (something wrong in backend)
      setError('Network error - make sure your backend is running') //error message
    } finally { //no matter if error or not
      setIsLoading(false) //stop showing loading state
    }
  }

//webpage structure
  return (
    //container for title
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8">
          Orchids Website Cloning
        </h1>
        {/* container for input section */}
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <label className="block text-sm font-medium mb-2">
            Enter Website URL:
          </label>
          <div className="flex gap-4"> {/* input field */}
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {/* input button */}
            <button 
              onClick={handleCloneWebsite}
              disabled={isLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? 'Cloning...' : 'Clone Website'} {/*button text*/}
            </button>
          </div>
          {/*error display*/}
          {error && (
            <p className="text-red-600 mt-2">{error}</p>
          )}
        </div>

        {/*preview section for cloned html*/}
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