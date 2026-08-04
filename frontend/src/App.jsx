import { use, useState } from 'react'

function App() {
  const[url, setUrl] = useState('')
  const[preview, setPreview] = useState(null)

async function handlePreviewClick() {
  const response = await fetch('http://127.0.0.1:8000/preview', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ url: url }),
  })
  const data = await response.json()
  setPreview(data)
}

async function handleDownloadClick() {
  const response = await fetch(`http://127.0.0.1:8000/download/${preview.id}`, {
    method: 'POST',
  })
  const data = await response.json()
  console.log(data)
  
}

 return (
  <div>
    <h1>Video Downloader</h1>
    <input
      type="text"
      value={url}
      onChange={(e) => setUrl(e.target.value)}
      placeholder='Paste a video URL'
    />
    <button onClick={handlePreviewClick}>Preview</button>

    {preview && (
      <div>
        <p>Status: {preview.status}</p>
        <img src={preview.thumbnail} alt={preview.title} width="200" />
        <p>{preview.title}</p>
        <button onClick={handleDownloadClick}>Download</button>
      </div>
    )}
  </div>
) 

}

export default App