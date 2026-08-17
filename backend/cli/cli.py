from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container, Center, VerticalScroll
from textual.widgets import ListView, ListItem, Label, Static, ContentSwitcher, Input

import os
import psycopg2
import time
import subprocess

from backend.db.db_connection import DATABASE_URL
from backend.db.db_operations import get_all_video_request
from backend.services.download_files import list_downloads, DOWNLOADS_DIR
from backend.services.video_download import preview_video
from backend.db.schema import CREATE_VIDEO_REQUESTS_TABLE
from backend.cli.thumbnail_art import get_thumbnail_art

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

class NavList(ListView, can_focus=False):
    """Tab strip: selection is driven by app-level bindings and mouse
    clicks, not ListView's own up/down cursor bindings."""


class VideoDownloader(App):
    CSS_PATH = "cli.tcss" #with textual, importing the styling is not needed
    AUTO_FOCUS = None  # url-input steal focus from nav shortcuts on mount
    BINDINGS = [
        ("escape", "go_home", "Home"),
        ("up, left, w, a, p", "nav_previous", "Previews"),
        ("down, right, s, d", "nav_next", "Downloads"),
    ]

    def __init__(self, conn):
        super().__init__()
        self.conn = conn

    def compose(self) -> ComposeResult:
        with Container(id="window"):
            yield NavList(
                ListItem(Label("Previews"), id="nav-previews"),
                ListItem(Label("Downloads"), id="nav-downloads"),
                id="nav",
                initial_index=None,
            )
            with ContentSwitcher(initial="home", id="main"):
                with Container(id="home"):
                    with Center():
                        yield Static("Video Downloader", id="home-title")
                    with Center():
                        yield Input(placeholder="Paste a video URL", id="url-input")
                yield Container(ListView(id="previews-list"), id="previews")
                with Horizontal(id="downloads"):
                    yield ListView(id="downloads-list")
                    with Container(id="details-panel"):
                        yield Static(id="details-thumbnail")
                        with VerticalScroll(id="details-description-scroll"):
                            yield Static(id="details-description")
        yield Static("NORMAL", id="statusline")

    def action_go_home(self) -> None:
        self.query_one("#main", ContentSwitcher).current = "home"
        self.query_one("#nav", ListView).index = None

    def action_nav_previous(self) -> None:
        self.query_one("#nav", ListView).index = 0

    def action_nav_next(self) -> None:
        self.query_one("#nav", ListView).index = 1

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "url-input":
            return
        url = event.value.strip()
        if not url:
            return

        status = self.query_one("#statusline", Static)
        try:
            preview_video(self.conn, url)
        except Exception:
            status.update("Could not process URL")
            status.add_class("-danger")
            return

        status.remove_class("-danger")
        status.update("NORMAL")
        event.input.value = ""
        self.query_one("#nav", ListView).index = 0

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.list_view.id == "nav":
            if event.item is None:
                return
            target = "downloads" if event.item.id == "nav-downloads" else "previews"
            self.query_one("#main", ContentSwitcher).current = target
            if target == "downloads":
                self.load_downloads()
            else:
                self.load_previews()
        elif event.list_view.id == "downloads-list":
            self.show_download_details(event.list_view.index)

    def load_previews(self) -> None:
        previews_list = self.query_one("#previews-list", ListView)
        previews_list.clear()
        for request_id, url, title, _thumbnail, _description in get_all_video_request(self.conn):
            previews_list.append(ListItem(Label(f"[{request_id}] {title or url}")))
        self.set_focus(previews_list)

    def load_downloads(self) -> None:
        downloads_list = self.query_one("#downloads-list", ListView)
        downloads_list.clear()
        self.downloads = list_downloads()
        for download in self.downloads:
            downloads_list.append(ListItem(Label(download["folder"])))
        self.set_focus(downloads_list)
        self.show_download_details(downloads_list.index)

    def show_download_details(self, index: int | None) -> None:
        thumbnail = self.query_one("#details-thumbnail", Static)
        description = self.query_one("#details-description", Static)
        if index is None or not (0 <= index < len(self.downloads)):
            thumbnail.update("")
            description.update("No download selected")
            return

        download = self.downloads[index]
        thumbnail_path = None
        if download["thumbnail_file"]:
            thumbnail_path = os.path.join(DOWNLOADS_DIR, download["folder"], download["thumbnail_file"])
        art = get_thumbnail_art(thumbnail_path)
        thumbnail.update(art or "No thumbnail available")
        description.update(download["description"] or "No description available")


def main():
    conn = setup_database()
    if conn is None:
        return
    app = VideoDownloader(conn)
    app.run()
    conn.close()

if __name__ == "__main__":
    main()