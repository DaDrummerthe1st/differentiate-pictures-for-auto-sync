"""Server-side HTML rendering for modules/web/server.py.

Deliberately no client-side JS: every page is plain HTML, thumbnails and
the annotated full-size image are both generated server-side (see
modules/web/imaging.py, modules/findings.py) and served as plain <img>
tags. Same pattern as contacts/web/render.py, kept independent of it -
modules/ doesn't depend on contacts/, same convention as
modules/quality.py and modules/objects.py.
"""
import os
from urllib.parse import quote

from modules.objects import DetectionResult
from modules.pictures import PictureLocation
from modules.quality import QualityResult

_PAGE_STYLE = """
body { font-family: sans-serif; max-width: 1000px; margin: 2rem auto; color: #222; }
h1 { margin-bottom: 0.3rem; }
form.scan { margin: 1.5rem 0; padding: 1rem; border: 1px solid #ddd; border-radius: 6px; }
form.scan label { display: block; margin-bottom: 0.6rem; }
form.scan input[type=text] { width: 100%; padding: 0.4rem; box-sizing: border-box; }
button, input[type=submit] { padding: 0.5rem 1rem; cursor: pointer; }
.error { color: #a33; }
nav.pager { display: flex; align-items: center; gap: 1rem; margin: 1rem 0; }
.grid { display: flex; flex-wrap: wrap; gap: 12px; }
.thumb-entry { position: relative; width: 200px; text-align: center; }
.thumb-entry img { max-width: 100%; border: 1px solid #ccc; border-radius: 4px; }
.thumb-entry .filename { font-size: 0.8em; color: #555; word-break: break-all; }
.has-objects-badge {
  position: absolute; top: 4px; right: 4px; background: #276b27; color: white;
  font-size: 0.75em; padding: 0.1rem 0.4rem; border-radius: 10px;
}
.detail-image { max-width: 100%; }
.section { margin: 1rem 0; }
.section h2 { font-size: 1em; margin-bottom: 0.3rem; }
.section ul { margin: 0; padding-left: 1.2rem; }
"""


def escape_html(s) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _pictures_url(folder: str, page: int) -> str:
    return f"/pictures?folder={quote(folder, safe='')}&page={page}"


def _page_shell(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{escape_html(title)}</title><style>{_PAGE_STYLE}</style></head>
<body>
{body}
</body>
</html>"""


def render_scan_page(message: str | None = None) -> str:
    error_html = f'<p class="error">{escape_html(message)}</p>' if message else ""
    body = f"""
<h1>modules/ pictures viewer</h1>
<p class="note">Scan a folder into the pictures register, then browse its findings.</p>
{error_html}
<form class="scan" method="post" action="/scan">
  <label>Folder path<input type="text" name="folder" required></label>
  <label>Source label (optional)<input type="text" name="source"></label>
  <input type="submit" value="Scan folder">
</form>
"""
    return _page_shell("modules/ pictures viewer", body)


def _thumb_entry(location: PictureLocation, has_objects: bool) -> str:
    badge = '<span class="has-objects-badge">objects</span>' if has_objects else ""
    filename = escape_html(os.path.basename(location.path))
    return f"""<a class="thumb-entry" href="/picture/{escape_html(location.location_id)}">
  {badge}
  <img src="/image/{escape_html(location.location_id)}?variant=thumb" alt="{filename}">
  <div class="filename">{filename}</div>
</a>"""


def _pager(folder: str, page: int, page_count: int, start_index: int, end_index: int, total_count: int) -> str:
    prev_link = f'<a href="{escape_html(_pictures_url(folder, page - 1))}">&lt; Prev</a>' if page > 0 else ""
    next_link = f'<a href="{escape_html(_pictures_url(folder, page + 1))}">Next &gt;</a>' if page < page_count - 1 else ""
    return f"""<nav class="pager">
  {prev_link}
  <span>{start_index}-{end_index} of {total_count} (page {page + 1}/{page_count})</span>
  {next_link}
</nav>"""


def render_grid_page(
    entries: list[tuple[PictureLocation, bool]],
    folder: str,
    page: int,
    page_count: int,
    start_index: int,
    end_index: int,
    total_count: int,
) -> str:
    pager = _pager(folder, page, page_count, start_index, end_index, total_count)
    grid = "\n".join(_thumb_entry(location, has_objects) for location, has_objects in entries)
    body = f"""
<h1>{escape_html(folder)}</h1>
<p><a href="/">&lt; scan another folder</a></p>
{pager}
<div class="grid">
{grid}
</div>
{pager}
"""
    return _page_shell(f"Pictures - {folder}", body)


def render_detail_page(
    location: PictureLocation,
    exif: list[str],
    quality: QualityResult,
    objects_result: DetectionResult,
    folder: str,
    page: int,
) -> str:
    if objects_result.detections:
        object_lines = "\n".join(
            f"<li>{escape_html(d.class_name)}  {d.confidence:.0%}  bbox={d.bbox}</li>" for d in objects_result.detections
        )
    else:
        object_lines = "<li>(none detected)</li>"
    exif_lines_html = "\n".join(f"<li>{escape_html(line)}</li>" for line in exif)

    body = f"""
<p><a href="{escape_html(_pictures_url(folder, page))}">&lt; back to grid</a></p>
<h1>{escape_html(os.path.basename(location.path))}</h1>
<img class="detail-image" src="/image/{escape_html(location.location_id)}?variant=full" alt="">
<div class="section">
  <h2>EXIF</h2>
  <ul>{exif_lines_html}</ul>
</div>
<div class="section">
  <h2>Quality</h2>
  <p>blur {quality.blur:.1f}%   exposure {quality.exposure:+.1f}%   saturation {quality.saturation:.1f}%</p>
</div>
<div class="section">
  <h2>Objects ({objects_result.image_width}x{objects_result.image_height})</h2>
  <ul>{object_lines}</ul>
</div>
"""
    return _page_shell(os.path.basename(location.path), body)
