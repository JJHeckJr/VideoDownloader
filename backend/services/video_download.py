import os
import urllib.request

import yt_dlp
from backend.db.db_operations import (
    create_video_request,
    get_video_request,
    get_video_request_by_url
)

def fetch_video_info(url):
    download_options = {}
    with yt_dlp.YoutubeDL(download_options) as ydl:
        info_dict = ydl.extract_info(url, download=False)
    title = info_dict.get('title', 'Unknown Title')
    thumbnail = info_dict.get('thumbnail', "Unknown Thumbnail")
    return title, thumbnail

def sanitize_filename(name):
    invalid_chars = '/\\:*?"<>|'
    for char in invalid_chars:
        name = name.replace(char, "_")
    return name

def preview_video(conn, url):
    existing = get_video_request_by_url(conn, url)
    if existing:
        return {"id": existing[0], "url": existing[1], "title": existing[2], "thumbnail": existing[3]}
    title, thumbnail = fetch_video_info(url)
    new_id = create_video_request(conn, url, title, thumbnail)
    return {"id": new_id, "url": url, "title": title, "thumbnail": thumbnail}


def show_progress(d):
    if d['status'] == 'downloading':
        try:
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
            percent = downloaded / total * 100
        except Exception:
            percent = 0
        filled = int(percent // 5)
        bar = "█" * filled + "-" * (20 - filled) #bar calculation
        print(f"\r[{bar}] {percent:.1f}%", end='', flush=True)
    elif d['status'] == 'finished':
        print("\r[" + "█" * 20 + "] 100.0% - Download complete!        ")

    
def download_video(conn, request_id, progress_hook=None):
    row = get_video_request(conn, request_id)
    if row is None:
        return None
    video_url = row[1]
    title = sanitize_filename(row[2])
    thumbnail_url = row[3]

    folder_path = f"downloads/{title}"
    counter = 1
    while os.path.exists(folder_path):
        folder_path = f"downloads/{title} ({counter})"
        counter += 1
    os.makedirs(folder_path)

    output_path = f"{folder_path}/{title}.mp4"
    download_opts = {
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'progress_hooks': [progress_hook or show_progress],
    }
    with yt_dlp.YoutubeDL(download_opts) as ydl:
        ydl.download([video_url])

    thumbnail_path = f"{folder_path}/{title}.jpg"
    urllib.request.urlretrieve(thumbnail_url, thumbnail_path)

    return True
  