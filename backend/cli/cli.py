from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import ListView, ListItem, Label, Static, Input

import psycopg2
import time 
import subprocess

from backend.db.db_connection import DATABASE_URL
from backend.db.db_operations import get_all_video_request
from backend.services.download_files import list_downloads
from backend.db.schema import CREATE_VIDEO_REQUESTS_TABLE

def setup_database():
    subprocess.run(["docker", "compose", "up", "-d"], check=True)

    for _ in range(10):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            break
        except psycopg2.OperationalError:
            print("Waiting for database to be ready...")
            time.sleep(1)

    else:
        print("Could not connect to the database")
        return None

    cur = conn.cursor()
    cur.execute(CREATE_VIDEO_REQUESTS_TABLE)
    conn.commit()
    return conn

class VideoDownloaderApp(App):
    CSS_PATH = "cli.tcss" #no need to manually import the css styling
    active_section = reactive("requests")

    def __init__(self, conn):
        super().__init__()
        self.conn = conn

    def on_mount(self) -> None:
        self.load_items()

    def compose(self) -> ComposeResult: #rendering similar to return in jsx
        with Horizontal(id="body"):
            yield ListView(
                ListItem(Label("Requests"), id="nav-requests"),
                ListItem(Label("Downloads"), id="nav-downloads"),
                id="nav",
            )
            yield ListView(id="item-list")
            yield Static("Select an item to see details", id="detail")

            
        yield Static("NORMAL  |  0 items", id="statusline") #from template textual module


    #tracks highlighted list
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.list_view.id == "nav" and event.item is not None:
            self.active_section = "downloads" if event.item.id == "nav-downloads" else "requests"
        elif event.list_view.id =="item-list" and event.item is not None:
            highlighted_index = event.list_view.index
            selected_item = self.current_items[highlighted_index]
            self.show_detail(selected_item)

    def show_detail(self, item) -> None:
        if self.active_section == "requests":
            detail_text = f"[{item['id']}] {item['title']}\n{item['url']}"
        else:
            detail_text = f"{item['folder']}\nVideo file: {item['video_file']}\nThumbnail file: {item['thumbnail_file']}"
        detail = self.query_one("#detail", Static)
        detail.update(detail_text)


    def watch_active_section(self, section: str) -> None:
        self.load_items()

    def load_items(self) -> None:
        items = []
        if self.active_section == "requests":
            rows = get_all_video_request(self.conn)
            for row in rows:
                request_id = row[0]
                url = row[1]
                title = row[2]
                if title:
                    display_text = title
                else:
                    display_text = url
                items.append({
                    "id": request_id,
                    "url": url,
                    "title": title,
                    "thumbnail": row[3],
                    "label": f"[{request_id}] {display_text}",
                })
        else:
            downloads = list_downloads()
            for download in downloads:
                folder_name = download["folder"]
                items.append({
                    "id": None,
                    "folder": folder_name,
                    "video_file": download["video_file"],
                    "thumbnail_file": download["thumbnail_file"],
                    "label": folder_name
                })
        item_list = self.query_one("#item-list", ListView)
        item_list.clear() #clears rows when switching from "Requests" or "Downloads"

        for item in items:
            item_list.append(ListItem(Label(item["label"])))

        section_name = self.active_section.capitalize()
        item_count = len(items)
        status = self.query_one("#statusline", Static) #getElementbyid count
        status.update(f"NORMAL | {section_name} | {item_count} items")
        self.current_items = items
        
def main():
    conn = setup_database()
    if conn is None:
        return
    app = VideoDownloaderApp(conn)
    app.run()
    conn.close()

if __name__ == "__main__":
    main()
