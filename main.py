from fastapi import FastAPI
from pydantic import BaseModel
import yt_dlp

#App Instance
app = FastAPI(
    title="Task Management API",
    description="API for managing tasks with FastAPI",
    version="0.1.0"

) 

class VideoSubmission(BaseModel):
    url: str

@app.get("/")
def read_homepage():
    return{"message": "Server is running!"}

@app.post("/preview")
def process_video_preview(payload: VideoSubmission):
#read data the user passed into endpoint
    user_url = payload.url

    dowload_options = {}

    try:
        with yt_dlp.YoutubeDL(dowload_options) as ydl:
            info_dict = ydl.extract_info(user_url, download=False)
            video_title = info_dict.get('title', 'Unknown Title')
            video_thumbnail = info_dict.get('thumbnail', '')

    #configure tool to read details without downloading
        return {
        "status": "Sucess",
        "title": video_title,
        "thumbnail": video_thumbnail
        }
    except Exception as e:
        return {
            "status": "Error",
            "message": f"Could not process url"
        }

