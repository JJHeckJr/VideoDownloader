export async function previewVideo(url) {
    const response = await fetch('http://127.0.0.1:8000/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({ url })
    })

    const data = await response.json()
    if (!response.ok) {
        throw new Error(data.detail)
    }
    return data
}

export async function getRequests() {
    const response = await fetch('http://127.0.0.1:8000/requests')
    const data = await response.json()
    if (!response.ok) {
        throw new Error(data.detail)
    }
    return data
}