import yt_dlp
from db_operations import create_video_request, get_video_request

def fetch_video_info(url):
    download_options = {}
    with yt_dlp.YoutubeDL(download_options) as ydl:
        info_dict = ydl.extract_info(url, download=False)
    title = info_dict.get('title', 'Unknown Title')
    thumbnail = info_dict.get('thumbnail', "Unknown Thumbnail")
    return title, thumbnail

def preview_video(conn, url):
    title, thumbnail = fetch_video_info(url)
    new_id = create_video_request(conn, url, title, thumbnail)
    return {"id": new_id, "url": url, "title": title, "thumbnail": thumbnail}
    
def download_video(conn, request_id):
    row = get_video_request(conn, request_id)
    if row is None:
        return None
    video_url = row[1]
    download_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s'
    }
    with yt_dlp.YoutubeDL(download_opts) as ydl:
        ydl.download([video_url])
    return True