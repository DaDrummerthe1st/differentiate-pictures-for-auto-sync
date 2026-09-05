"""Local-only server for browsing modules/ pictures/quality/objects findings
in a browser - the same viewing experience as modules/test_main.py's tkinter
dev tool, server-rendered instead: pick a folder (scanned into the existing
pictures/locations SQLite register via modules.pictures), browse it as a
paginated thumbnail grid, click through to a per-picture detail page with
EXIF/quality/objects findings and the annotated full-size image.

All real logic - scanning, DB queries, quality/objects detection, image
resizing/annotation, HTML rendering - is Python. The browser only ever
requests plain HTML pages and images; no client-side JS. Nothing goes
further than 127.0.0.1. Same pattern as contacts/web/server.py, kept
independent of it - modules/ doesn't depend on contacts/.

Run manually: python3 -m modules.web.server
Then open:    http://127.0.0.1:8766/
"""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, parse_qsl, quote, urlsplit

from modules.findings import annotate, exif_lines
from modules.objects import detect_objects
from modules.pictures import DEFAULT_DB_PATH, GetListOfValidPictureFiles, get_location, list_locations_under
from modules.quality import check_all
from modules.web.imaging import encode_jpeg, thumbnail
from modules.web.render import render_detail_page, render_grid_page, render_scan_page

DEFAULT_PORT = 8766
IMAGES_PER_PAGE = 20  # same X-server-pixmap-exhaustion rationale as modules/test_main.py
THUMBNAIL_MAX_SIZE = 220
MAX_DISPLAY_WIDTH = 900


def _pictures_redirect_url(folder: str, page: int) -> str:
    return f"/pictures?folder={quote(folder, safe='')}&page={page}"


def handle_scan_page(message: str | None = None) -> str:
    return render_scan_page(message=message)


def handle_scan(folder: str, source: str, db_path: str = DEFAULT_DB_PATH) -> str:
    """Registers every picture under folder into the DB. Returns the URL to
    redirect the browser to. Raises ValueError if folder doesn't exist."""
    if not os.path.isdir(folder):
        raise ValueError(f"No such folder: {folder}")
    GetListOfValidPictureFiles(folder, source=source or None, db_path=db_path)
    return _pictures_redirect_url(folder, 0)


def handle_grid(query_string: str, db_path: str = DEFAULT_DB_PATH) -> str:
    params = parse_qs(query_string)
    folder = params.get("folder", [""])[0]
    requested_page = int(params.get("page", ["0"])[0])

    locations = list_locations_under(folder, db_path=db_path)
    if not locations:
        return render_scan_page(message=f"No pictures registered under {folder}")

    page_count = -(-len(locations) // IMAGES_PER_PAGE)  # ceil division
    page = max(0, min(requested_page, page_count - 1))
    start = page * IMAGES_PER_PAGE
    page_locations = locations[start : start + IMAGES_PER_PAGE]
    entries = [(location, bool(detect_objects(location.path).detections)) for location in page_locations]

    return render_grid_page(
        entries,
        folder=folder,
        page=page,
        page_count=page_count,
        start_index=start + 1,
        end_index=min(start + IMAGES_PER_PAGE, len(locations)),
        total_count=len(locations),
    )


def handle_detail(location_id: str, db_path: str = DEFAULT_DB_PATH, folder: str = "", page: str = "0") -> str:
    location = get_location(location_id, db_path=db_path)
    if location is None:
        raise ValueError(f"No such picture: {location_id}")

    quality = check_all(location.path)
    result = detect_objects(location.path)
    lines = exif_lines(location.path)
    return render_detail_page(
        location, exif=lines, quality=quality, objects_result=result, folder=folder, page=int(page)
    )


def handle_image(location_id: str, variant: str, db_path: str = DEFAULT_DB_PATH) -> bytes:
    location = get_location(location_id, db_path=db_path)
    if location is None:
        raise ValueError(f"No such picture: {location_id}")

    if variant == "thumb":
        image = thumbnail(location.path, max_size=THUMBNAIL_MAX_SIZE)
    else:
        result = detect_objects(location.path)
        image = annotate(location.path, result, max_display_width=MAX_DISPLAY_WIDTH)
    return encode_jpeg(image)


class PicturesRequestHandler(BaseHTTPRequestHandler):
    def _respond_html(self, body: str, status: int = 200) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _respond_jpeg(self, image_bytes: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(image_bytes)))
        self.end_headers()
        self.wfile.write(image_bytes)

    def _redirect(self, url: str) -> None:
        self.send_response(303)
        self.send_header("Location", url)
        self.end_headers()

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length)

    def do_GET(self):
        split = urlsplit(self.path)
        if split.path in ("/", "/index.html"):
            self._respond_html(handle_scan_page())
        elif split.path == "/pictures":
            self._respond_html(handle_grid(split.query))
        elif split.path.startswith("/picture/"):
            params = parse_qs(split.query)
            location_id = split.path[len("/picture/") :]
            try:
                html = handle_detail(
                    location_id,
                    folder=params.get("folder", [""])[0],
                    page=params.get("page", ["0"])[0],
                )
                self._respond_html(html)
            except ValueError as exc:
                self._respond_html(handle_scan_page(message=str(exc)), status=404)
        elif split.path.startswith("/image/"):
            params = parse_qs(split.query)
            location_id = split.path[len("/image/") :]
            variant = params.get("variant", ["thumb"])[0]
            try:
                self._respond_jpeg(handle_image(location_id, variant))
            except ValueError:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/scan":
            body = self._read_body().decode("utf-8")
            form = dict(parse_qsl(body))
            try:
                redirect_url = handle_scan(form.get("folder", ""), form.get("source", ""))
                self._redirect(redirect_url)
            except ValueError as exc:
                self._respond_html(handle_scan_page(message=str(exc)), status=400)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Default logging prints the request line (path only, never bodies)
        # to stderr; suppressed to keep this a quiet local tool.
        pass


def main(port: int = DEFAULT_PORT) -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", port), PicturesRequestHandler)
    print(f"Pictures findings viewer: http://127.0.0.1:{port}/  (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
