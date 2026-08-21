from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container, Center, VerticalScroll
from textual.widgets import ListView, ListItem, Label, Static, ContentSwitcher, Input, Footer, TextArea

import os
import psycopg2

from backend.db.db_connection import DATABASE_URL, setup_database
from backend.db.db_operations import get_all_video_request, delete_video_request, update_video_request
from backend.services.download_files import list_downloads, delete_download, DOWNLOADS_DIR
from backend.services.video_download import preview_video, download_video, fetch_video_info
from backend.cli.thumbnail_art import get_thumbnail_art

class NavList(ListView, can_focus=False):
    """Tab strip: selection is driven by app-level bindings and mouse
    clicks, not ListView's own up/down cursor bindings."""

class PreviewsList(ListView):
    """Adds a delete key on top of ListView's normal up/down/enter behavior.
    """
    BINDINGS = [
        ("delete, backspace", "delete_selected", "Delete"),
        ("w", "cursor_up", "Up"),
        ("s", "cursor_down", "Down"),
        ("u", "edit_selected", "Edit"),
    ]

    def action_delete_selected(self) -> None:
        self.app.delete_selected_preview()

    def action_edit_selected(self) -> None:
        self.app.edit_selected_preview()

class DownloadsList(ListView):
    """Adds a delete key on top of ListView's normal up/down/enter behvavior
    """
    BINDINGS = [
        ("delete, backspace", "delete_selected", "Delete"),
        ("w", "cursor_up", "Up"),
        ("s", "cursor_down", "Down"),
    ]

    def action_delete_selected(self) -> None:
        self.app.delete_selected_download()
class VideoDownloader(App):
    CSS_PATH = "cli.tcss" #with textual, importing the styling is not needed
    AUTO_FOCUS = None  # url-input steal focus from nav shortcuts on mount
    BINDINGS = [
        ("escape", "go_home", "Home"),
        ("up, left, w, a, p", "nav_previous", "Previews"),
        ("down, right, s, d", "nav_next", "Downloads"),
        ("h", "toggle_footer", "Toggle Keys"),
        ("ctrl+s", "save_edit", "Save Edit"),
    ]

    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self._editing_preview_id = None

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
                with Horizontal(id="previews"):
                    yield PreviewsList(id="previews-list")
                    with Container(id="preview-details-panel"):
                        yield Static(id="preview-details-thumbnail")
                        with VerticalScroll(id="preview-details-description-scroll"):
                            yield Static(id="preview-details-description")
                    with Container(id="preview-edit-form"):
                        yield Input(placeholder="Title", id="edit-title-input")
                        yield Input(placeholder="URL", id="edit-url-input")
                        yield Static(
                            "Note: changing the URL will re-fetch the title, thumbnail, and description automatically.",
                            id="edit-url-hint",
                        )
                        yield TextArea(id="edit-description-input")
                with Horizontal(id="downloads"):
                    yield DownloadsList(id="downloads-list")
                    with Container(id="details-panel"):
                        yield Static(id="details-thumbnail")
                        with VerticalScroll(id="details-description-scroll"):
                            yield Static(id="details-description")
        with Container(id="footer-bar"):
            yield Footer()
            yield Static("NORMAL", id="statusline")

    def action_go_home(self) -> None:
        if self._editing_preview_id is not None:
            self.cancel_preview_edit()
            return
        self.query_one("#main", ContentSwitcher).current = "home"
        self.query_one("#nav", ListView).index = None

    def action_toggle_footer(self) -> None:
        footer = self.query_one(Footer)
        footer.display = not footer.display

    def action_nav_previous(self) -> None:
        self.query_one("#nav", ListView).index = 0

    def action_nav_next(self) -> None:
        self.query_one("#nav", ListView).index = 1

    def action_save_edit(self) -> None:
        if self._editing_preview_id is not None:
            self.save_preview_edit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id in ("edit-title-input", "edit-url-input"):
            self.save_preview_edit()
            return
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
        elif event.list_view.id == "previews-list":
            self.show_preview_details(event.list_view.index)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id != "previews-list":
            return
        index = event.list_view.index
        if index is None or not (0 <= index < len(self.previews)):
            return
        self.download_preview(self.previews[index]["id"])

    def download_preview(self, request_id: int) -> None:
        status = self.query_one("#statusline", Static)
        status.remove_class("-danger")
        status.update("Downloading")
        self.run_worker(
            lambda: self._download_preview_worker(request_id),
            thread=True,
            exclusive=True,
            group="download",
        )

    def _download_preview_worker(self, request_id: int) -> None:
        worker_conn = psycopg2.connect(DATABASE_URL)
        try:
            success = download_video(worker_conn, request_id, progress_hook=self._on_download_progress)
        except Exception:
            success = False
        finally:
            worker_conn.close()
        self.call_from_thread(self._on_download_finished, success)

    def _on_download_progress(self, d) -> None:
        if d['status'] != 'downloading':
            return
        try:
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
            percent = downloaded / total * 100
        except Exception:
            percent = 0
        self.call_from_thread(self._update_download_progress, percent)

    def _update_download_progress(self, percent: float) -> None:
        status = self.query_one("#statusline", Static)
        filled = int(percent // 5)
        bar = "█" * filled + "-" * (20 - filled)
        status.update(f"Downloading [{bar}] {percent:.0f}%")


    def _on_download_finished(self, success: bool) -> None:
        status = self.query_one("#statusline", Static)
        if success:
            status.remove_class("-danger")
            status.update("NORMAL")
        else:
            status.add_class("-danger")
            status.update("Download failed")

    def delete_selected_preview(self) -> None:
        previews_list = self.query_one("#previews-list", ListView)
        index = previews_list.index
        if index is None or not (0 <= index < len(self.previews)):
            return
        delete_video_request(self.conn, self.previews[index]["id"])
        self.load_previews()

    def edit_selected_preview(self) -> None:
        previews_list = self.query_one("#previews-list", ListView)
        index = previews_list.index
        if index is None or not (0 <= index < len(self.previews)):
            return
        preview = self.previews[index]
        self._editing_preview_id = preview["id"]
        self._editing_original_url = preview["url"]

        self.query_one("#edit-title-input", Input).value = preview["title"] or ""
        self.query_one("#edit-url-input", Input).value = preview["url"] or ""
        self.query_one("#edit-description-input", TextArea).text = preview["description"] or ""

        self.query_one("#preview-details-panel").display = False
        self.query_one("#preview-edit-form").display = True
        self.set_focus(self.query_one("#edit-title-input", Input))

    def cancel_preview_edit(self) -> None:
        self.query_one("#preview-edit-form").display = False
        self.query_one("#preview-details-panel").display = True
        self._editing_preview_id = None
        self.set_focus(self.query_one("#previews-list", ListView))


    def save_preview_edit(self) -> None:
        request_id = self._editing_preview_id
        if request_id is None:
            return

        new_title = self.query_one("#edit-title-input", Input).value().strip()
        new_url = self.query_one("#edit-url-input", Input).value().strip()
        new_description = self.query_one("edit-description-input", TextArea).text
        status = self.query_one("statusline", Static)

        if not new_title or not new_url:
            try:
                new_title, new_thumbnail, new_description = fetch_video_info(new_url)
            except Exception:
                status.update("Could not fetch new URL")
                status.add_class("-danger")
                return
        else:
            preview = next(p for p in self.previews if p["id"] == request_id)
            new_thumbnail = preview["thumbnail"]

        update_video_request(self.conn, request_id, new_url, new_title, new_thumbnail, new_description)
        status.remove_class("-danger")
        status.update("NORMAL")
        self.cancel_preview_edit()
        self.load_previews()

    def load_previews(self) -> None:
        previews_list = self.query_one("#previews-list", ListView)
        previews_list.clear()
        self.previews = []
        for request_id, url, title, thumbnail, description in get_all_video_request(self.conn):
            self.previews.append({
                "id": request_id,
                "url": url,
                "title": title,
                "thumbnail": thumbnail,
                "description": description
            })
            previews_list.append(ListItem(Label(f"[{request_id}] {title or url}", classes="list-label")))
        self.set_focus(previews_list)
        self.show_preview_details(previews_list.index)

    def show_preview_details(self, index: int | None) -> None:
        panel = self.query_one("#preview-details-panel")
        thumbnail = self.query_one("#preview-details-thumbnail", Static)
        description = self.query_one("#preview-details-description", Static)
        if index is None or not (0 <= index < len(self.previews)):
            panel.add_class("-empty")
            thumbnail.update("")
            description.update("No preview selected")
            return

        panel.remove_class("-empty")
        preview = self.previews[index]
        art = get_thumbnail_art(preview["thumbnail"], width=67)
        thumbnail.update(art or "No thumbnail available")
        description.update(preview["description"] or "No description available")

    def delete_selected_download(self) -> None:
        downloads_list = self.query_one("#downloads-list", ListView)
        index = downloads_list.index
        if index is None or not (0 <= index < len(self.downloads)):
            return
        delete_download(self.downloads[index]["folder"])
        self.load_downloads()

    def load_downloads(self) -> None:
        downloads_list = self.query_one("#downloads-list", ListView)
        downloads_list.clear()
        self.downloads = list_downloads()
        for download in self.downloads:
            downloads_list.append(ListItem(Label(download["folder"], classes="list-label")))
        self.set_focus(downloads_list)
        self.show_download_details(downloads_list.index)

    def show_download_details(self, index: int | None) -> None:
        panel = self.query_one("#details-panel")
        thumbnail = self.query_one("#details-thumbnail", Static)
        description = self.query_one("#details-description", Static)
        if index is None or not (0 <= index < len(self.downloads)):
            panel.add_class("-empty")
            thumbnail.update("")
            description.update("No download selected")
            return

        panel.remove_class("-empty")
        download = self.downloads[index]
        thumbnail_path = None
        if download["thumbnail_file"]:
            thumbnail_path = os.path.join(DOWNLOADS_DIR, download["folder"], download["thumbnail_file"])
        art = get_thumbnail_art(thumbnail_path, width=67)
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