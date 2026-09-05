# Extract shared EXIF/annotate helpers from test_main.py into modules/findings.py

First step of building a browser-based pictures viewer (mirroring modules/test_main.py's tkinter dev
tool): pulled its EXIF-reading and detection-annotation logic (including the EXIF-rotation-matching
assertion) out into modules/findings.py, tested directly, so the upcoming web viewer reuses the exact
same code instead of duplicating that subtlety a second time. test_main.py now imports from it;
behavior unchanged.

- **Doc size**: no docs changed.
