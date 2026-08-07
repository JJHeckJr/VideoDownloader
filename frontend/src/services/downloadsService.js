export async function downloadVideo(requestId) {
    const response = await fetch(`http://127.0.0.1:8000/download/${requestId}`, {
        method: 'POST',
    })
    const data = await response.json()
    if (!response.ok) {
        throw new Error(data.detail)
    }
    return data
}

export async function getDownloads() {
    const response = await fetch(`http://127.0.0.1:8000/downloads`)
    const data = await response.json() 
    if (!response.ok) {
        throw new Error(data.detail)
    }
    return data
}

export async function deleteDownload(folderName) {
    const response = await fetch(`http://127.0.0.1:8000/downloads/${folderName}`, {
        method: 'DELETE',
    })
    const data = await response.json()
    if (!response.ok) {
        throw new Error(data.detail)
    }
    return data
}