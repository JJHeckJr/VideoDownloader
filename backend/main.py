from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import yt_dlp
from backend.db.db_connection import get_db
from backend.services.video_download import preview_video, download_video
from backend.services.download_files import list_downloads, delete_download
from backend.db.db_operations import (
create_video_request, 
get_video_request, 
update_video_request,
delete_video_request,
get_all_video_request,
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


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

app.mount("/downloads-static", StaticFiles(directory="downloads"), name="downloads-static") #given url, look for file in downloads folder and send contents back

class VideoSubmission(BaseModel):
    url: str

@app.get("/")
def read_homepage():
    return{"message": "Server is running!"}

@app.post("/preview")
def process_video_preview(payload: VideoSubmission, db = Depends(get_db)): #Depends used for dependency injection
    try:
        result = preview_video(db, payload.url) #preview video needs a database connection and url
        return {"status": "Success", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not process url")


@app.get("/requests")
def read_all_video_requests(db = Depends(get_db)):
    rows = get_all_video_request(db)
    result = []
    for row in rows:
        result.append({"id": row[0], "url": row[1], "title": row[2], "thumbnail": row[3], "description": row[4]})
    return result

@app.get("/requests/{request_id}")
def read_video_request(request_id: int, db = Depends(get_db)):
    row = get_video_request(db, request_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Request not found") #404 status code means not found
    return {
        "id": row[0],
        "url": row[1],
        "title": row[2],
        "thumbnail": row[3],
        "description": row[4]
    }

class VideoUpdate(BaseModel):
    url: str
    title: str
    thumbnail: str
    description: str

@app.put("/requests/{request_id}")
def update_request(request_id: int, payload: VideoUpdate, db = Depends(get_db)): #used for dependency injections for functions
    updated = update_video_request(db, request_id, payload.url, payload.title, payload.thumbnail, payload.description)
    if updated == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    return {
        "status": "Success",
        "id": request_id,
        "url": payload.url,
        "title": payload.title,
        "description": payload.description,
    }

@app.delete("/requests/{request_id}")
def delete_request(request_id: int, db = Depends(get_db)):
    deleted = delete_video_request(db, request_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    return{"status": "Success", "message": f"Request {request_id} deleted"}

@app.post("/download/{request_id}")
def download_video_endpoint(request_id: int, db = Depends(get_db)):
        row = get_video_request(db, request_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Request not found")
        try:
            download_video(db, request_id)
            return {
                "status": "Success",
                "message": f"Video downloaded for request {request_id}"}
        except Exception as e:
            raise HTTPException(status_code=400, detail="Could not download video")

@app.get("/downloads")
def read_downloads():
    return list_downloads()

@app.delete("/downloads/{folder_name}")
def delete_download_endpoint(folder_name: str):
    deleted = delete_download(folder_name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Download not found")
    return {"status": "Success", "message": f"Deleted {folder_name}"}