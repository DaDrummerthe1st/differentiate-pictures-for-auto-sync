"""Local-only server for the contacts-import demo.

Runs the real, tested contacts.google_csv_import.parse_google_csv() against
an uploaded file, instead of a second hand-rolled parser living in the demo
page's JS. Nothing goes further than 127.0.0.1: the browser posts the file
to this process, this process never forwards it anywhere.

Run manually: python3 -m contacts.demo.server
Then open:    http://127.0.0.1:8765/
"""

import csv
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from contacts.google_csv_import import parse_google_csv

DEMO_DIR = Path(__file__).parent
DEFAULT_PORT = 8765


def parse_csv_to_json(csv_text: str) -> str:
    contacts = parse_google_csv(csv_text)
    return json.dumps(
        [{"display_name": c.display_name, "emails": c.emails} for c in contacts]
    )


class DemoRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = (DEMO_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/parse":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        csv_text = self.rfile.read(length).decode("utf-8")
        try:
            body = parse_csv_to_json(csv_text).encode("utf-8")
        except (csv.Error, UnicodeDecodeError) as exc:
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(str(exc).encode("utf-8"))
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Default logging prints the request line (path only, never the
        # uploaded body) to stderr; suppressed to keep this a quiet local tool.
        pass


def main(port: int = DEFAULT_PORT) -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", port), DemoRequestHandler)
    print(f"Contacts-import demo: http://127.0.0.1:{port}/  (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
