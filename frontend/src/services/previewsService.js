export async function previewVideo(url) {
    const response = await fetch(`http://127.0.0.1:8000/preview`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ url }),
    })
    const data = await response.json()
    if (!response.ok) {
        throw new Error(data.detail)
    }
    return data
}

export async function getPreviews() {
    const response = await fetch(`http://127.0.0.1:8000/requests`)
    const data = await response.json()
    if (!response.ok) {
        throw new Error(data.detail)
    }
    return data
}

export async function getPreview(requestId) {
    const response = await fetch(`http://127.0.0.1:8000/requests/${requestId}`)
    const data = await response.json()
    if (!response.ok) {
        throw new Error(data.detail)
    }
    return data
}

export async function updatePreview(requestId, { url, title, thumbnail, description }) {
    const response = await fetch(`http://127.0.0.1:8000/requests/${requestId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, title, thumbnail, description }),
    })
    const data = await response.json()
    if (!response.ok) {
        throw new Error(data.detail)
    }
    return data
}

export async function deletePreview(requestId) {
    const response = await fetch(`http://127.0.0.1:8000/requests/${requestId}`, {
        method: 'DELETE',
    })
    const data = await response.json()
    if (!response.ok) {
        throw new Error(data.detail)
    }
    return data
}