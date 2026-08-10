import { use, useState } from 'react'
import '../styles/App.css'
import Sidebar from './Sidebar'
import Downloads from './Downloads'
import { getRequests, previewVideo } from '../services/requestsService'
import { downloadVideo } from '../services/downloadsService'

function App() {
  const[url, setUrl] = useState('')
  const[preview, setPreview] = useState(null)
  const [requests, setRequests] = useState()
  const [error, setError] = useState(null)
  const [activeView, setActiveView] = useState('home')
  const [downloadMessage, setDownloadMessage] = useState(null)

async function handlePreviewClick() {
try {
  const data = await previewVideo(url)
  setError(null)
  setPreview(data)
} catch (err) {
  setError(err.message || 'Could not reach the server')
  setPreview(null)
}
}

async function handleDownloadClick() {
  try {
    const data = await downloadVideo(preview.id)
    setDownloadMessage(data.message)
  } catch(err) {
    setError(err.message || 'Could not reach the server')
    setDownloadMessage(null)
  }
}

async function handleViewRequestsClick() {
  try {
    const data = await getRequests()
    setRequests(data)
  } catch (err) {
    setError(err.message || 'Could not reach the server.')
  }
}

 return (
  <>
  <Sidebar onNavigate={setActiveView}/>
  <div className='app'>
    <h1>Video Downloader</h1>
    {activeView === 'downloads' ? (
      <Downloads />
    ) : (
      <div className="home-content">
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
            {downloadMessage && <p>{downloadMessage}</p>}
          </div>
        )}
        <pre>{JSON.stringify(requests, null, 2)}</pre>
      </div>
    )}
  </div>
  </>
)

}

export default App
