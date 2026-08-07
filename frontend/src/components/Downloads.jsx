import { useState, useEffect } from 'react'

function Downloads() {
    const [downloads, setDownloads] = useState([])
    const [error, setError] = useState(null)

    useEffect(() => {
        fetchDownloads()
    }, [])

    async function fetchDownloads() {
        try {
            const response = await fetch('http://127.0.0.1:8000/downloads')
            const data = await response.json()
            if (!response.ok) {
                setError(data.detail)
                return
            }
            setError(null)
            setDownloads(data)
        } catch (err) {
            setError('Could not reach the server.')
        }
    }

    async function handleDelete(folderName) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/downloads/${folderName}`, {
                method: 'DELETE',
            })
            const data = await response.json()
            if (!response.ok) {
                setError(data.detail)
                return
            }
            fetchDownloads()
        } catch (err) {
            setError('Could not reach the server.')
        }
    }

    return (
        <div className="downloads">
            <h2>Downloads</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {downloads.map((item) => (
                <div key={item.folder} className="download-item">
                    <p>{item.folder}</p>
                    <button onClick={() => handleDelete(item.folder)}>Delete</button>
                </div>
            ))}
        </div>
    )
}

export default Downloads
