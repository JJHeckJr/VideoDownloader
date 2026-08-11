import os
import shutil

DOWNLOADS_DIR = "downloads"

def list_downloads():
    downloads = []
    for entry in os.listdir(DOWNLOADS_DIR):
        folder_path = os.path.join(DOWNLOADS_DIR, entry)
        if os.path.isdir(folder_path):
            video_file = None
            thumbnail_file = None
            for filename in os.listdir(folder_path):
                if filename.endswith(".mp4"):
                    video_file = filename
                elif filename.endswith(".jpg"):
                    thumbnail_file = filename
            downloads.append({
                "folder": entry,
                "video_file": video_file,
                "thumbnail_file": thumbnail_file
            })
    return downloads

def delete_download(folder_name):
    folder_path = os.path.join(DOWNLOADS_DIR, folder_name)
    if not os.path.isdir(folder_path):
        return False
    shutil.rmtree(folder_path)
    return True