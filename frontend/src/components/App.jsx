import { use, useState } from 'react'
import '../styles/App.css'
import Sidebar from './Sidebar'

function App() {
  const[url, setUrl] = useState('')
  const[preview, setPreview] = useState(null)
  const [requests, setRequests] = useState()
  const [error, setError] = useState(null)
  const [activeView, setActiveView] = useState('home')

async function handlePreviewClick() {
try {
  const response = await fetch('http://127.0.0.1:8000/preview', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ url: url }),
  })
  const data = await response.json()
  if (!response.ok) {
    setError(data.detail)
    setPreview(null)
    return
  }
  setError(null)
  setPreview(data)
} catch(err) {
  setError('Could not reach the server.')
  setPreview(null)

  }
}

async function handleDownloadClick() {
  const response = await fetch(`http://127.0.0.1:8000/download/${preview.id}`, {
    method: 'POST',
  })
  const data = await response.json()
  console.log(data)
}

async function handleViewRequestsClick() {
  const response = await fetch('http://127.0.0.1:8000/requests')
  const data = await response.json()
  setRequests(data)
}

 return (
  <>
  <Sidebar onNavigate={setActiveView}/>
  <div className='app'>
    <h1>Video Downloader</h1>
    <p>Current view: {activeView}</p>
    <div className="input-row">
    <input
      type="text"
      value={url}
      onChange={(e) => setUrl(e.target.value)}
      placeholder='Paste a video URL'
    />
    <button onClick={handlePreviewClick}>Preview</button>
  </div>
  {error && <p style={{ color: 'red' }}>{error}</p>}

    {preview && (
      <div className='preview-card'>
        <p>Status: {preview.status}</p>
        <img src={preview.thumbnail} alt={preview.title} width="200" />
        <p>{preview.title}</p>
        <div className="button-row">
          <button onClick={handleDownloadClick}>Download</button>
          <button onClick={handleViewRequestsClick}>View Past Requests</button>
        </div>
      </div>
    )}
    <pre>{JSON.stringify(requests, null, 2)}</pre>
  </div>
  </>
)

}

export default App