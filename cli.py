import subprocess
import time
import psycopg2
from database import DATABASE_URL
from models import CREATE_VIDEO_REQUESTS_TABLE
from video_download import fetch_video_info, preview_video, download_video
from db_operations import get_video_request, get_all_video_request, update_video_request, delete_video_request

BANNER = """
========================================
||   YOUTUBE VIDEO DOWNLOADER (CLI)   ||
========================================
"""

def setup_databse():
    subprocess.run(["docker", "compose", "up", "-d"], check=True)

    for attempt in range(10):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            break
        except psycopg2.OperationalError:
            print("Waiting for databse to be ready...")
            time.sleep(1)
    else:
        print("Could not connect to the database")
        return None

    cur = conn.cursor()
    cur.execute(CREATE_VIDEO_REQUESTS_TABLE)
    conn.commit()
    cur.close()
    return conn

def main():
    print(BANNER)
    conn = setup_databse()
    if conn is None:
        return
    while True:
        command = input(
            "Please enter a command:\n"
            "preview\n"
            "download\n"
            "get\n"
            "list\n"
            "update\n"
            "delete\n"
            "quit\n"
            "> "
            ).strip().lower()

        if command == "preview":
            url = input("Enter the video URL: ").strip()
            result = preview_video(conn, url)
            print("-" * 40)
            print(f"Saved as id {result['id']}")
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Thumbnail: {result['thumbnail']}")
            print("-" * 40)

        elif command == "download":
            user_input = input("Please enter a video URL or an existing request id: ").strip()
            try:
                if user_input.isdigit():
                    request_id = int(user_input)
                else:
                    result = preview_video(conn, user_input)
                    request_id = result["id"]
                    print(f"Saved as new request id {request_id}")
                success = download_video(conn, request_id)
                if success is None:
                    print("No request found with that id.")
                else:
                    print("Download complete.")
            except Exception as e:
                print("Could not process that url.")

        elif command == "get":
            request_id = int(input("Enter the request id: ").strip())
            row = get_video_request(conn, request_id)
            if row is None:
                print(f"No request found with request id: {request_id}")
            else:
                print("-" * 40)
                print(f"[{row[0]}] {row[2]}")
                print(f"    {row[1]}")
                print("-" * 40)

        elif command == "list":
            rows = get_all_video_request(conn)
            print("-" * 40)
            for row in rows:
                print(f"[{row[0]}] {row[2]}")
                print(f"    {row[1]}")
            print("-" * 40)

        elif command == "update":
            request_id = int(input("Enter the request id: ").strip())
            existing_id = get_video_request(conn, request_id)
            if existing_id is None:
                print("No request found with that id.")
            else:
                url = input("Enter the new url: ").strip()
                try:
                    title, thumbnail = fetch_video_info(url)
                    update_video_request(conn, request_id, url, title, thumbnail)
                    print("Update successful.")
                except Exception as e:
                    print("Could not process url")

        elif command == "delete": 
            request_id = int(input("Enter the request id: ").strip())
            deleted = delete_video_request(conn, request_id)
            if deleted == 0:
                print("No request found with that id.")
            else:
                print("Delete successful.")

        elif command == "quit":
            break
        else:
            print("Unkown command, try again.")
    conn.close()
if __name__ == "__main__":
    main()


