"""Local-only server for contacts import/browse: served by Python, handled
by Python, all real logic (CSV parsing, dedup/merge classification,
persistence, HTML rendering) in Python. The browser only ever submits plain
HTML forms and displays the HTML this server renders back — no
client-side JS, no business logic duplicated in a second language.

Nothing goes further than 127.0.0.1: the browser posts a file straight to
this process, which never forwards it anywhere.

Run manually: python3 -m contacts.web.server
Then open:    http://127.0.0.1:8765/
"""
import csv
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, parse_qsl, urlsplit

from contacts.db import DEFAULT_DB_PATH, classify_contacts, list_all_contacts, save_contacts
from contacts.google_csv_import import parse_google_csv
from contacts.models import Contact
from contacts.multipart import extract_uploaded_file
from contacts.render import render_browse_page, render_preview_page, render_saved_page, render_upload_page
from contacts.search import DEFAULT_SEARCH_FIELDS, available_search_fields, filter_contacts

DEFAULT_PORT = 8765


def handle_preview(csv_bytes: bytes, db_path: str = DEFAULT_DB_PATH) -> str:
    contacts = parse_google_csv(csv_bytes.decode("utf-8"))
    results = classify_contacts(contacts, db_path=db_path)
    return render_preview_page(results)


def handle_save(contacts_json: str, db_path: str = DEFAULT_DB_PATH) -> str:
    contacts = [
        Contact(display_name=c["display_name"], emails=c["emails"], source=c["source"], raw=c["raw"])
        for c in json.loads(contacts_json)
    ]
    results = save_contacts(contacts, db_path=db_path)
    counts = {"new": 0, "updated": 0, "unchanged": 0}
    for r in results:
        counts[r.status] += 1
    return render_saved_page(counts)


def handle_browse(query_string: str, db_path: str = DEFAULT_DB_PATH) -> str:
    all_contacts = list_all_contacts(db_path=db_path)
    params = parse_qs(query_string)
    query = params.get("q", [""])[0]
    available_fields = available_search_fields(all_contacts)
    submitted = params.get("submitted", ["0"])[0] == "1"
    selected_fields = params.get("field", []) if submitted else list(DEFAULT_SEARCH_FIELDS)
    filtered = filter_contacts(all_contacts, query, selected_fields)
    return render_browse_page(
        filtered,
        total_count=len(all_contacts),
        query=query,
        selected_fields=selected_fields,
        available_fields=available_fields,
    )


class ContactsRequestHandler(BaseHTTPRequestHandler):
    def _respond_html(self, body: str, status: int = 200) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length)

    def do_GET(self):
        split = urlsplit(self.path)
        if split.path in ("/", "/index.html"):
            self._respond_html(render_upload_page())
        elif split.path == "/contacts":
            self._respond_html(handle_browse(split.query))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/preview":
            content_type = self.headers.get("Content-Type", "")
            body = self._read_body()
            try:
                _filename, csv_bytes = extract_uploaded_file(content_type, body)
                self._respond_html(handle_preview(csv_bytes))
            except (ValueError, csv.Error, UnicodeDecodeError) as exc:
                self._respond_html(render_upload_page(message=f"Could not read that file: {exc}"), status=400)
        elif self.path == "/save":
            body = self._read_body().decode("utf-8")
            form = dict(parse_qsl(body))
            try:
                self._respond_html(handle_save(form.get("contacts_json", "[]")))
            except (ValueError, KeyError) as exc:
                self._respond_html(render_upload_page(message=f"Could not save: {exc}"), status=400)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Default logging prints the request line (path only, never bodies)
        # to stderr; suppressed to keep this a quiet local tool.
        pass


def main(port: int = DEFAULT_PORT) -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", port), ContactsRequestHandler)
    print(f"Contacts import/browse: http://127.0.0.1:{port}/  (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
