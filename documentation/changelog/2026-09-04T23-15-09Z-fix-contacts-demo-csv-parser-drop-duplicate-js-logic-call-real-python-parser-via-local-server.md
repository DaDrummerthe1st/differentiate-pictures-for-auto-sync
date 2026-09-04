# Fix contacts demo CSV parser: drop duplicate JS logic, call real Python parser via local server

The previous session's demo page (`contacts/demo/index.html`) duplicated `google_csv_import.py`'s
parsing logic in hand-rolled JS that split rows on plain commas — it misparsed Joakim's real
121-column Google export wherever a quoted field (address, notes) contained a literal comma.
Rather than write a second, RFC-4180-aware JS parser that could drift from the Python one again,
removed the JS parser entirely and added `contacts/demo/server.py` (stdlib-only, no framework):
the demo's "Import CSV" button now posts the file to a local `/parse` endpoint that calls the real,
already-tested `parse_google_csv()`. One parser, not two. 3 new tests plus a regression test
locking in the comma-in-field case (19 total, all passing); Joakim verifies against his real export
himself in his own browser (this session never touches it — server has to be started manually).

- **Doc size**: contacts/README.md 2383 -> 3285 chars (+902).
