import './App.css'
import { use, useState } from 'react'

function App() {
  const[url, setUrl] = useState('')
  const[preview, setPreview] = useState(null)
  const [requests, setRequests] = useState()

async function handlePreviewClick() {
  const response = await fetch('http://127.0.0.1:8000/preview', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ url: url }),
  })
  const data = await response.json()
  setPreview(data)
  console.log(data)
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
  <div className='app'>
    <h1>Video Downloader</h1>
    <div className="input-row">
    <input
      type="text"
      value={url}
      onChange={(e) => setUrl(e.target.value)}
      placeholder='Paste a video URL'
    />
    <button onClick={handlePreviewClick}>Preview</button>
  </div>

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
) 

}

export default App