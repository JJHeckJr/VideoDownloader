import os
import shutil

from backend.services.video_download import sanitize_filename

DOWNLOADS_DIR = "downloads"

def list_downloads():
    downloads = []
    for entry in os.listdir(DOWNLOADS_DIR):
        folder_path = os.path.join(DOWNLOADS_DIR, entry)
        if os.path.isdir(folder_path):
            video_file = None
            thumbnail_file = None
            description_file = None
            for filename in os.listdir(folder_path):
                if filename.endswith(".mp4"):
                    video_file = filename
                elif filename.endswith(".jpg"):
                    thumbnail_file = filename
                elif filename.endswith(".txt"):
                    description_file = filename

            description = None
            if description_file:
                with open(os.path.join(folder_path, description_file), "r", encoding="utf-8") as f:
                    description = f.read()

            downloads.append({
                "folder": entry,
                "video_file": video_file,
                "thumbnail_file": thumbnail_file,
                "description": description
            })
    return downloads

def delete_download(folder_name):
    folder_path = os.path.join(DOWNLOADS_DIR, folder_name)
    if not os.path.isdir(folder_path):
        return False
    shutil.rmtree(folder_path)
    return True

def rename_download(folder_name, new_title):
    old_folder_path = os.path.join(DOWNLOADS_DIR, folder_name)
    if not os.path.isdir(old_folder_path):
        return None

    sanitize_title = sanitize_filename(new_title)
    new_folder_path = os.path.join(DOWNLOADS_DIR, sanitize_title)
    counter = 1
    while os.path.exists(new_folder_path) and new_folder_path != old_folder_path:
        new_folder_path = os.path.join(DOWNLOADS_DIR, f"{sanitize_title} ({counter})")
        counter += 1

    if new_folder_path == old_folder_path:
        return folder_name

    for filename in os.listdir(old_folder_path):
        _, ext = os.path.splitext(filename)
        if ext.lower() in (".mp4", ".jpg", ".txt"):
            os.rename (
                os.path.join(old_folder_path, filename),
                os.path.join(old_folder_path, f"{sanitize_title}{ext}")
            )
    os.rename(old_folder_path, new_folder_path)
    return os.path.basename(new_folder_path)