# Add thumbnail imaging and HTML rendering for the pictures web viewer

Third step of the browser-based pictures viewer. modules/web/imaging.py generates plain scaled-down
thumbnails (no boxes) for the grid view, reusing modules/findings.annotate for the full-size
bounding-box image in detail view. modules/web/render.py renders three pages, server-rendered HTML
only, no client-side JS: a folder-scan form, a paginated thumbnail grid (a small badge overlay marks
photos with detected objects - plain HTML/CSS, no re-encoded image), and a per-picture detail page
with EXIF/quality/objects findings. All tested; no server wiring yet, that's the next step.

- **Doc size**: no docs changed.
