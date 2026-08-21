import { useState, useEffect } from 'react'
import '../styles/Previews.css'
import { getPreviews, deletePreview } from '../services/previewsService'

function Previews() {
    const [previews, setPreviews] = useState([])
    const [error, setError] = useState(null)
    const [openMenu, setOpenMenu] = useState(null)

    useEffect(() => {
        fetchPreviews()
    }, [])

    async function fetchPreviews() {
        try {
            const data = await getPreviews()
            setError(null)
            setPreviews(data)
        } catch (err) {
            setError(err.message || 'Could not reach the server.')
        }
    }

    async function handleDelete(requestId) {
        try {
            await deletePreview(requestId)
            fetchPreviews()
        } catch (err) {
            setError(err.message || 'Could not reach the server.')
        }
    }

    return (
        <div>
            <h2>Previews</h2>
            {error && <p className="previews-error">{error}</p>}
            {!error && previews.length === 0 && (
                <p className="previews-empty">No saved previews yet.</p>
            )}
            <div className="previews">
                {previews.map((item) => (
                    <div key={item.id} className="preview-list-card">
                        <img
                            className="preview-list-card__image"
                            src={item.thumbnail}
                            alt="Preview"
                        />
                        <div className="preview-list-card__scrim"></div>
                        <div className="preview-list-card__body">
                            <h3 className="preview-list-card__title">{item.title}</h3>
                        </div>
                        <button
                            className="preview-list-card__menu-button"
                            onClick={() => setOpenMenu(openMenu === item.id ? null : item.id)}
                        >
                            ⋮
                        </button>
                        {openMenu === item.id && (
                            <div className="preview-list-card__menu">
                                <button
                                    className="preview-list-card__menu-item"
                                    onClick={() => handleDelete(item.id)}
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
export default Previews
