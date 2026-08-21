## VideoDownloader Description

Downloads videos from a URL, stores them locally with their metadata, browses them in a web UI or from the command line.

## Prerequisites
- Python 3.13+
- Docker (for Postgres database)
- Node.js + npm (for the frontend dev server, Web UI only)

## Setup
From project root with a virtual environment activated:

```
pip install -e .
```

This installs the project's dependencies and creates `videodownloader-cli` and `videodownloader-web` commands.

## Usage

```
videodownloader-cli
```
Single command automatically starts the Postgres container (via Docker Compose), creates the databse table if it doesn't already exist, launches the interactive CLI.

Available commands inside the CLI:

- `preview`: fetch and save a video's title/thumbnail from a URL
- `download`: download a video (by URL or existing request id)
- `get`: view a single saved request
- `list`: view all saved requests
- `update` update a saved request's info
- `delete`: remove a saved request
- `quit`: exit 

## Web UI
React frontend, backed by the FastAPI server (`backend/main.py`). Run both together with:
```
videodownloader-web
```
This starts the backend and the frontend dev server together, and stops both cleanly on Ctrl+C.

(First time only: run `npm install` inside `frontend/` before using this command.)

`pip install -e .` installs `fastapi` and `uvicorn` along with the rest of the backend's dependencies, so no separate install step is needed for the API server.