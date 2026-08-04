from fastapi import FastAPI, Depends
from pydantic import BaseModel
import yt_dlp
from database import get_db
from db_operations import (
create_video_request, 
get_video_request, 
update_video_request,
delete_video_request
)

from fastapi.middleware.cors import CORSMiddleware


#App Instance
app = FastAPI(
    title="Task Management API",
    description="API for managing tasks with FastAPI",
    version="0.1.0"

) 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoSubmission(BaseModel):
    url: str

@app.get("/")
def read_homepage():
    return{"message": "Server is running!"}

@app.post("/preview")
def process_video_preview(payload: VideoSubmission, db = Depends(get_db)): #Depends used for cleanup
#read data the user passed into endpoint
    user_url = payload.url

    download_options = {}

    try:
        with yt_dlp.YoutubeDL(download_options) as ydl:
            info_dict = ydl.extract_info(user_url, download=False)
            video_title = info_dict.get('title', 'Unknown Title')
            video_thumbnail = info_dict.get('thumbnail', '')

            new_row_id = create_video_request(db, user_url, video_title, video_thumbnail)

    #configure tool to read details without downloading
        return {
        "status": "Success",
        "title": video_title,
        "thumbnail": video_thumbnail,
        "id": new_row_id
        }
    except Exception as e:
        return {
            "status": "Error",
            "message": f"Could not process url",
            "debug": str(e)
        }

@app.get("/requests/{request_id}")
def read_video_request(request_id: int, db = Depends(get_db)):
    row = get_video_request(db, request_id)
    if row is None:
        return {"status": "Error", 
                "message": "Request not found"}
    return {
        "id": row[0],
        "url": row[1],
        "title": row[2],
        "thumbnail": row[3]
    }

class VideoUpdate(BaseModel):
    url: str
    title: str
    thumbnail: str

@app.put("/requests/{request_id}")
def update_request(request_id: int, payload: VideoUpdate, db = Depends(get_db)):
    updated = update_video_request(db, request_id, payload.url, payload.title, payload.thumbnail)
    if updated == 0:
        return {"status": "Error", "message": "Request not found"}
    return {
        "status": "Success",
        "id": request_id,
        "url": payload.url,
        "title": payload.title,
    }

@app.delete("/requests/{request_id}")
def delete_request(request_id: int, db = Depends(get_db)):
    deleted = delete_video_request(db, request_id)
    if deleted == 0:
        return {"status": "Error", "message": "Request not found"}
    return{"status": "Success", "message": f"Request {request_id} deleted"}

@app.post("/download/{request_id}")
def download_video(request_id: int, db = Depends(get_db)):
    row = get_video_request(db, request_id)
    if row is None:
        return {"status": "Error", "message": "Requests not found"}

    video_url = row[1]
    download_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s'
    }

    try:
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            ydl.download([video_url])
        return {"status": "Success", "message": f"Video downloaded for request {request_id}"}
    except Exception as e:
        return {"status": "Error", "message": "Could not download video", "debug": str(e)}
