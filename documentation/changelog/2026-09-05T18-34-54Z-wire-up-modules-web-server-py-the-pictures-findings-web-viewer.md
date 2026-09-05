# Wire up modules/web/server.py, the pictures findings web viewer

Final step of the browser-based pictures viewer (modules/test_main.py's tkinter dev tool, in a
browser): modules/web/server.py, an http.server-based local server mirroring contacts/web/'s
pattern (stdlib only, no framework, no client-side JS). GET / (folder-scan form) → POST /scan
(registers the folder into modules.pictures's SQLite register, redirects) → GET /pictures?folder=&page=
(paginated thumbnail grid) → GET /picture/<location_id> (EXIF/quality/objects findings, full-size
annotated image) → GET /image/<location_id>?variant=thumb|full (JPEG bytes, generated per request).
Every handler function is tested directly (handle_scan/handle_grid/handle_detail/handle_image), same
convention as contacts/tests/test_web_server.py - no real HTTP server started for tests. Updated
modules/README.md and documentation/data-modeling/PICTURES_PIPELINE.md to describe the new tool and
its two read-only pictures.py query helpers.

- **Doc size** (Unicode codepoints): `modules/README.md` 3,120 → 4,804 (+1,684); `documentation/data-modeling/PICTURES_PIPELINE.md` 8,946 → 9,394 (+448).
