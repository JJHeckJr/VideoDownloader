import { useState, useEffect } from 'react'
import '../styles/Downloads.css'
import { getDownloads, deleteDownload } from '../services/downloadsService'

function Downloads() {
    const [downloads, setDownloads] = useState([])
    const [error, setError] = useState(null)
    const [openMenu, setOpenMenu] = useState(null)

    useEffect(() => {
        fetchDownloads()
    }, [])

    async function fetchDownloads() {
        try {
            const data = await getDownloads()
            setError(null)
            setDownloads(data)
        } catch (err) {
            setError(err.message || 'Could not reach the server.')
        }
    }

    async function handleDelete(folderName) {
        try {
            await deleteDownload(folderName)
            fetchDownloads()
        } catch (err) {
            setError(err.message || 'Could not reach the server.')
        }
    }

    return (
        <div>
            <h2>Downloads</h2>
            {error && <p className="downloads-error">{error}</p>}
            {!error && downloads.length === 0 && (
                <p className="downloads-empty">No downloads yet.</p>
            )}
            {/*could refactor to download component*/}
            <div className="downloads">
                {downloads.map((item) => (
                    <div key={item.folder} className="download-card">
                        <img
                            className="download-card__image"
                            src={`http://127.0.0.1:8000/downloads-static/${item.folder}/${item.thumbnail_file}`}
                            alt={item.folder}
                        />
                        <div className="download-card__scrim"></div>
                        <div className="download-card__play">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M8 5v14l11-7z" />
                            </svg>
                        </div>
                        <div className="download-card__body">
                            <h3 className="download-card__title">{item.folder}</h3>
                        </div>
                        <button
                            className="download-card__menu-button"
                            onClick={() => setOpenMenu(openMenu === item.folder ? null : item.folder)}
                            aria-label={`Options for ${item.folder}`}
                        >
                            ⋮
                        </button>
                        {openMenu === item.folder && (
                            <div className="download-card__menu">
                                <button
                                    className="download-card__menu-item"
                                    onClick={() => {
                                        handleDelete(item.folder)
                                        setOpenMenu(null)
                                    }}
                                >
                                    Delete
                                </button>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}

export default Downloads
