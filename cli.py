import os
import urllib.request
import subprocess
import time
import psycopg2
from thumbnail_art import image_to_color_blocks
from database import DATABASE_URL
from models import CREATE_VIDEO_REQUESTS_TABLE
from video_download import fetch_video_info, preview_video, download_video
from db_operations import (
    get_video_request, 
    get_all_video_request, 
    update_video_request, 
    delete_video_request
)

BANNER = """
========================================
||   YOUTUBE VIDEO DOWNLOADER (CLI)   ||
========================================
"""

def setup_databse():
    subprocess.run(["docker", "compose", "up", "-d"], check=True)

    for _ in range(10):
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
"""
==============================
| Please enter a command :)  |
|----------------------------|
| - Preview                  |
| - Download                 |
| - Get Video                |
| - List All                 |
| - Update Row               |
| - Delete Entry             |
| - Quit                     |
==============================
"""
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

            #apply art to terminal
            temp_thumbnail_path = "temp_thumbnail.jpg"
            urllib.request.urlretrieve(result['thumbnail'], temp_thumbnail_path)
            print(image_to_color_blocks(temp_thumbnail_path))
            os.remove(temp_thumbnail_path)

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
            except Exception:
                print("Could not process that url.")

        elif command == "get":
            request_id = int(input("Enter the request id: ").strip())
            row = get_video_request(conn, request_id)
            if row is None:
                print(f"No request found with request id: {request_id}")
            else:
                line1 = f"[{row[0]}] {row[2]}"
                line2 = f"    {row[1]}"
                width = max(len(line1), len(line2))
                print("╭" + "─" * (width + 2) + "╮")
                print("│ " + line1.ljust(width) + " │")
                print("│ " + line2.ljust(width) + " │")
                print("╰" + "─" * (width + 2) + "╯")

        elif command == "list":
            rows = get_all_video_request(conn)
            print("▬" * 40)
            print("YOUR SAVED REQUESTS")
            print("▬" * 40)
            for row in rows:
                print(f"  • [{row[0]}] {row[2]}")
                print(f"      {row[1]}")
                print("  ")
            print("▬" * 40)

        elif command == "update":
            request_id = int(input("Enter the request id: ").strip())
            existing_row = get_video_request(conn, request_id)
            if existing_row is None:
                print("No request found with that id.")
            else:
                old_title = existing_row[2]
                old_url = existing_row[1]
                url = input("Enter the new url: ").strip()
                try:
                    title, thumbnail = fetch_video_info(url)
                    update_video_request(conn, request_id, url, title, thumbnail)
                    print("~" * 40)
                    print(f"  UPDATED REQUEST #{request_id}")
                    print("~" * 40)
                    print("  Before:")
                    print(f"  [{request_id}] {old_title}")
                    print(f"      {old_url}")
                    print("  After:")
                    print(f"  [{request_id}] {title}")
                    print(f"      {url}")
                    print("~" * 40)
                except Exception:
                    print("Could not process url")

        elif command == "delete":
            request_id = int(input("Enter the request id: ").strip())
            row = get_video_request(conn, request_id)
            if row is None:
                print("No request found with that id.")
            else:
                delete_video_request(conn, request_id)
                print(" ")
                print(" ")
                print(f"  DELETED REQUEST #{request_id}")
                print("x" * 40)
                print(f"  [{row[0]}] {row[2]}")
                print(f"      {row[1]}")
                print("x" * 40)

        elif command == "quit":
            break
        else:
            print("Unkown command, try again.")
    conn.close()
if __name__ == "__main__":
    main()


