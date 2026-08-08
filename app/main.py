import hashlib
import json
import mimetypes
import os
import sqlite3
import threading
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageDraw, ImageOps
from pydantic import BaseModel

from app.auth import has_valid_session, load_auth_config, require_session, require_session_with_role

load_auth_config()

# The fixed boundary directory - individual photo sources (dpfas_media,
# momfiles, ...) are its direct subdirectories, each its own bind mount in
# docker-compose.prod.yml (momfiles read-only; dpfas_media read-write, the
# only one this app ever writes into itself - see UPLOAD_SOURCE_NAME
# below). Which one is actually served is the app_settings.active_source
# row below, not this constant - this only bounds where a source is
# allowed to live on disk.
PHOTOS_LIBRARY_ROOT = Path(os.environ.get("PHOTOS_LIBRARY_ROOT", "/photo-library-root")).resolve()
DEFAULT_ACTIVE_SOURCE = "dpfas_media"
# POST /api/upload always writes here, regardless of app_settings.active_source
# - if an admin has switched the active (served) source to momfiles at
# upload time, an upload must still never land there. Deliberately a
# separate constant from DEFAULT_ACTIVE_SOURCE above even though they
# share a value today - upload destination and "what's currently browsed"
# are different concerns that just happen to coincide by default.
UPLOAD_SOURCE_NAME = "dpfas_media"
# Resource-exhaustion guard, same shape as detector/main.py's
# MAX_UPLOAD_BYTES/_read_capped (documentation/security/THREATS.md #16) -
# checked in chunks, before a full read is ever attempted.
MAX_PHOTO_UPLOAD_BYTES = int(os.environ.get("MAX_PHOTO_UPLOAD_BYTES", str(25 * 1024 * 1024)))
_UPLOAD_READ_CHUNK_BYTES = 1024 * 1024
THUMB_CACHE = Path(os.environ.get("THUMB_CACHE_DIR", "/thumbcache"))
THUMB_CACHE.mkdir(parents=True, exist_ok=True)

# Caps concurrent Pillow decode+resize+encode calls - measured, allocated,
# released per POLICY.md's resource-efficiency rule. Each generation is a
# real memory/CPU spike; letting an unbounded number run at once on a
# 2-core, memory-tight host (see HARDWARE.md) is what was silently
# killing this container in production (2026-07-17 - see
# documentation/bugs/repo/under_process/2026-07-17-thumbnail-oom-under-load.md).
# Cache-hit serving (the common case after warmup) is NOT gated by this -
# only the expensive generation path is.
MAX_CONCURRENT_THUMBNAILS = int(os.environ.get("MAX_CONCURRENT_THUMBNAILS", "2"))
_thumb_semaphore = threading.Semaphore(MAX_CONCURRENT_THUMBNAILS)

STORY_DIR = Path(os.environ.get("STORY_DIR", "/stories"))
STORY_DIR.mkdir(parents=True, exist_ok=True)

PICTURE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp"}
VIDEO_EXTS = {".avi", ".mp4", ".mov", ".mkv", ".webm"}
DOCUMENT_EXTS = {".pdf"}
MEDIA_EXTS = PICTURE_EXTS | VIDEO_EXTS | DOCUMENT_EXTS
THUMB_SIZE = (340, 340)

DB_PATH = Path(os.environ.get("ANALYTICS_DB_PATH", "/data/analytics.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
db = sqlite3.connect(DB_PATH, check_same_thread=False)
# Guards every request-time use of `db` below - a single sqlite3.Connection
# shared across FastAPI's threadpool (check_same_thread=False) isn't safe
# under real concurrent access from multiple threads without this: caught
# 2026-08-08 when adding a second concurrent DB read to the /thumb path
# (get_active_photos_root(), for the admin photo-source setting) made
# test_thumb_concurrency.py's existing two-simultaneous-requests test
# flake with a corrupted read (a NOT NULL column read back as None) - the
# request-logging middleware below was already touching `db` on every
# request, unlocked, so the race was always latent, just never visibly
# triggered by a single unlocked reader before. Only the module-load-time
# schema setup above this line is exempt - it runs once, single-threaded,
# before the server accepts any requests.
_db_lock = threading.Lock()
db.execute(
    """
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        method TEXT NOT NULL,
        path TEXT NOT NULL,
        user_agent TEXT,
        client_ip TEXT
    )
    """
)
db.execute(
    """
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        event_type TEXT NOT NULL,
        detail TEXT,
        client_ip TEXT
    )
    """
)
db.execute(
    """
    CREATE TABLE IF NOT EXISTS voiceovers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        audio_filename TEXT NOT NULL,
        events_json TEXT NOT NULL,
        client_ip TEXT
    )
    """
)
# One tag = one fact about one photo, for one user. Keyed by photo_path
# (not a photo_id foreign key) because this app has no photo-catalog
# database at all - it reads /photos straight off disk. See
# documentation/tags/SCHEMA.md for the eventual Postgres entities/
# tag_references design this is a deliberately lighter-weight stand-in
# for, once Phase 2/3 ingestion exists.
# bbox_x/y/w/h are all NULL together (a whole-photo tag) or all set
# together (a region tag) - normalized 0..1 fractions of the image's
# own width/height, so they render correctly at any display size.
# source distinguishes 'manual' (built here) from 'auto' (future
# detector-written rows - not produced by anything yet, but the column
# exists now so next session's auto-tagging can write into this same
# table without a schema change).
db.execute(
    """
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        photo_path TEXT NOT NULL,
        category TEXT NOT NULL,
        value TEXT NOT NULL,
        bbox_x REAL,
        bbox_y REAL,
        bbox_w REAL,
        bbox_h REAL,
        source TEXT NOT NULL DEFAULT 'manual',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """
)
db.execute("CREATE INDEX IF NOT EXISTS idx_tags_photo_path ON tags(photo_path)")
# Singleton row (id is always 1) - which PHOTOS_LIBRARY_ROOT subdirectory
# is currently served. Admin-only (see GET/PUT /api/settings/photos-source
# below); a member never sees or changes this.
db.execute(
    """
    CREATE TABLE IF NOT EXISTS app_settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        active_source TEXT NOT NULL DEFAULT 'dpfas_media',
        updated_at TEXT NOT NULL
    )
    """
)
db.execute(
    "INSERT OR IGNORE INTO app_settings (id, active_source, updated_at) VALUES (1, ?, ?)",
    (DEFAULT_ACTIVE_SOURCE, datetime.now(timezone.utc).isoformat()),
)
db.commit()


def _log_event(event_type: str, detail: str = "", client_ip: str | None = None) -> None:
    with _db_lock:
        db.execute(
            "INSERT INTO events (ts, event_type, detail, client_ip) VALUES (?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), event_type, detail, client_ip),
        )
        db.commit()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _log_event("server_started")
    yield
    _log_event("server_stopping")


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)


class Event(BaseModel):
    type: str
    detail: str = ""


@app.post("/api/event")
def log_event(event: Event, request: Request):
    _log_event(event.type, event.detail, request.client.host if request.client else None)
    return {"ok": True}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    with _db_lock:
        db.execute(
            "INSERT INTO requests (ts, method, path, user_agent, client_ip) VALUES (?, ?, ?, ?, ?)",
            (
                datetime.now(timezone.utc).isoformat(),
                request.method,
                request.url.path,
                request.headers.get("user-agent"),
                request.client.host if request.client else None,
            ),
        )
        db.commit()
    return response


def _available_photo_sources() -> list[str]:
    if not PHOTOS_LIBRARY_ROOT.is_dir():
        return []
    return sorted(entry.name for entry in PHOTOS_LIBRARY_ROOT.iterdir() if entry.is_dir())


def _get_active_source() -> str:
    with _db_lock:
        row = db.execute("SELECT active_source FROM app_settings WHERE id = 1").fetchone()
    return row[0] if row else DEFAULT_ACTIVE_SOURCE


def get_active_photos_root() -> Path:
    candidate = (PHOTOS_LIBRARY_ROOT / _get_active_source()).resolve()
    # Same traversal-guard shape as resolve_relpath below - active_source
    # only ever reaches the DB via the PUT endpoint's `available` check,
    # but re-validate here too rather than trusting that invariant blindly.
    if candidate.parent != PHOTOS_LIBRARY_ROOT:
        raise HTTPException(status_code=500, detail="invalid active photo source configuration")
    return candidate


class PhotosSourceUpdate(BaseModel):
    active: str


@app.get("/api/settings/photos-source")
def get_photos_source(session: tuple[int, str] = Depends(require_session_with_role)):
    _, role = session
    if role != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    return {"active": _get_active_source(), "available": _available_photo_sources()}


@app.put("/api/settings/photos-source")
def set_photos_source(
    update: PhotosSourceUpdate, session: tuple[int, str] = Depends(require_session_with_role)
):
    _, role = session
    if role != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    if update.active not in _available_photo_sources():
        raise HTTPException(status_code=400, detail="unknown photo source")
    now = datetime.now(timezone.utc).isoformat()
    with _db_lock:
        db.execute(
            "INSERT INTO app_settings (id, active_source, updated_at) VALUES (1, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET active_source = excluded.active_source, updated_at = excluded.updated_at",
            (update.active, now),
        )
        db.commit()
    return {"active": _get_active_source(), "available": _available_photo_sources()}


def resolve_relpath(relpath: str) -> Path:
    root = get_active_photos_root()
    candidate = (root / relpath).resolve()
    if root not in candidate.parents and candidate != root:
        raise HTTPException(status_code=400, detail="invalid path")
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return candidate


# The four entity-bearing categories (documentation/tags/TAXONOMY.md) plus
# activity/occasion and a free-text catch-all - a deliberately narrowed
# slice of the full 12-category taxonomy for this first build pass.
# occasion added 2026-08-05 on direct request ("tag them with peoples
# names, places, occasions etc") - it's one of the "plain tags" (category
# + value, no entity/bounding-box), so no new mechanism was needed. The
# remaining 7 (quality, privacy, relationships, story/narrative,
# temporal/seasonal, co-presence/group, origin - the last already built
# separately as kind='album') are still out of scope, not forgotten.
TAG_CATEGORIES = {"people", "places", "objects", "animals", "occasion", "generic"}


class TagCreate(BaseModel):
    photo_path: str
    category: str
    value: str
    bbox_x: float | None = None
    bbox_y: float | None = None
    bbox_w: float | None = None
    bbox_h: float | None = None


class TagUpdate(BaseModel):
    category: str
    value: str
    bbox_x: float | None = None
    bbox_y: float | None = None
    bbox_w: float | None = None
    bbox_h: float | None = None


def _validate_tag_fields(category: str, value: str, bbox_x, bbox_y, bbox_w, bbox_h) -> str:
    if category not in TAG_CATEGORIES:
        raise HTTPException(status_code=400, detail="unknown category")
    value = value.strip()
    if not value:
        raise HTTPException(status_code=400, detail="value must not be blank")
    bbox_fields = (bbox_x, bbox_y, bbox_w, bbox_h)
    if any(f is not None for f in bbox_fields) and any(f is None for f in bbox_fields):
        raise HTTPException(status_code=400, detail="bounding box requires x, y, w, and h together")
    if all(f is not None for f in bbox_fields):
        if not (0 <= bbox_x <= 1 and 0 <= bbox_y <= 1):
            raise HTTPException(status_code=400, detail="bounding box x/y must be within 0..1")
        if bbox_w <= 0 or bbox_h <= 0:
            raise HTTPException(status_code=400, detail="bounding box w/h must be positive")
        if bbox_x + bbox_w > 1 or bbox_y + bbox_h > 1:
            raise HTTPException(status_code=400, detail="bounding box must stay within the image")
    return value


def _tag_row_to_dict(row) -> dict:
    (tag_id, category, value, bbox_x, bbox_y, bbox_w, bbox_h, source, created_at, updated_at) = row
    bbox = None
    if bbox_x is not None:
        bbox = {"x": bbox_x, "y": bbox_y, "w": bbox_w, "h": bbox_h}
    return {
        "id": tag_id,
        "category": category,
        "value": value,
        "bbox": bbox,
        "source": source,
        "created_at": created_at,
        "updated_at": updated_at,
    }


_TAG_SELECT_COLUMNS = "id, category, value, bbox_x, bbox_y, bbox_w, bbox_h, source, created_at, updated_at"


@app.get("/api/tags")
def list_tags(p: str = Query(...), session: tuple[int, str] = Depends(require_session_with_role)):
    user_id, role = session
    resolve_relpath(p)
    with _db_lock:
        if role == "admin":
            rows = db.execute(
                f"SELECT {_TAG_SELECT_COLUMNS} FROM tags WHERE photo_path = ? ORDER BY id",
                (p,),
            ).fetchall()
        else:
            rows = db.execute(
                f"SELECT {_TAG_SELECT_COLUMNS} FROM tags WHERE photo_path = ? "
                "AND (user_id = ? OR source = 'auto') ORDER BY id",
                (p, user_id),
            ).fetchall()
    return [_tag_row_to_dict(row) for row in rows]


@app.get("/api/tags/values")
def tag_value_suggestions(
    category: str = Query(...), session: tuple[int, str] = Depends(require_session_with_role)
):
    user_id, role = session
    if category not in TAG_CATEGORIES:
        raise HTTPException(status_code=400, detail="unknown category")
    with _db_lock:
        if role == "admin":
            rows = db.execute(
                "SELECT value, COUNT(*) AS c FROM tags WHERE category = ? "
                "GROUP BY value ORDER BY c DESC, value COLLATE NOCASE",
                (category,),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT value, COUNT(*) AS c FROM tags WHERE (user_id = ? OR source = 'auto') AND category = ? "
                "GROUP BY value ORDER BY c DESC, value COLLATE NOCASE",
                (user_id, category),
            ).fetchall()
    return [row[0] for row in rows]


@app.post("/api/tags", status_code=201)
def create_tag(tag: TagCreate, user_id: int = Depends(require_session)):
    resolve_relpath(tag.photo_path)
    value = _validate_tag_fields(tag.category, tag.value, tag.bbox_x, tag.bbox_y, tag.bbox_w, tag.bbox_h)
    now = datetime.now(timezone.utc).isoformat()
    with _db_lock:
        cur = db.execute(
            "INSERT INTO tags (user_id, photo_path, category, value, bbox_x, bbox_y, bbox_w, bbox_h, "
            "source, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'manual', ?, ?)",
            (user_id, tag.photo_path, tag.category, value, tag.bbox_x, tag.bbox_y, tag.bbox_w, tag.bbox_h, now, now),
        )
        db.commit()
        row = db.execute(f"SELECT {_TAG_SELECT_COLUMNS} FROM tags WHERE id = ?", (cur.lastrowid,)).fetchone()
    return _tag_row_to_dict(row)


@app.patch("/api/tags/{tag_id}")
def update_tag(tag_id: int, tag: TagUpdate, user_id: int = Depends(require_session)):
    value = _validate_tag_fields(tag.category, tag.value, tag.bbox_x, tag.bbox_y, tag.bbox_w, tag.bbox_h)
    now = datetime.now(timezone.utc).isoformat()
    with _db_lock:
        existing = db.execute("SELECT id FROM tags WHERE id = ? AND user_id = ?", (tag_id, user_id)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="not found")
        db.execute(
            "UPDATE tags SET category = ?, value = ?, bbox_x = ?, bbox_y = ?, bbox_w = ?, bbox_h = ?, "
            "updated_at = ? WHERE id = ?",
            (tag.category, value, tag.bbox_x, tag.bbox_y, tag.bbox_w, tag.bbox_h, now, tag_id),
        )
        db.commit()
        row = db.execute(f"SELECT {_TAG_SELECT_COLUMNS} FROM tags WHERE id = ?", (tag_id,)).fetchone()
    return _tag_row_to_dict(row)


@app.delete("/api/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int, user_id: int = Depends(require_session)):
    with _db_lock:
        cur = db.execute("DELETE FROM tags WHERE id = ? AND user_id = ?", (tag_id, user_id))
        db.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="not found")
    return Response(status_code=204)


@app.get("/api/tree")
def api_tree(_: int = Depends(require_session)):
    headlines: dict[str, dict[str, list[str]]] = {}
    root = get_active_photos_root()

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in MEDIA_EXTS:
            continue
        expected = _EXPECTED_LABEL_FOR_EXT.get(path.suffix.lower())
        if expected:
            with path.open("rb") as f:
                header = f.read(64)
            if _sniff_file_type(header) != expected:
                # Extension claims one thing, actual content says
                # another - don't show it as if it were a real photo.
                # Still visible via /api/file-summary's mismatch list.
                continue
        rel = path.relative_to(root)
        parent_parts = rel.parent.parts
        if not parent_parts:
            headline, chunk = ".", "."
        else:
            headline = parent_parts[0]
            chunk = "/".join(parent_parts)
        headlines.setdefault(headline, {}).setdefault(chunk, []).append(rel.as_posix())

    result = []
    for headline in sorted(headlines, key=str.lower):
        chunks = headlines[headline]
        result.append(
            {
                "headline": headline,
                "chunks": [
                    {"path": chunk, "images": sorted(chunks[chunk], key=str.lower)}
                    for chunk in sorted(chunks, key=str.lower)
                ],
            }
        )
    return JSONResponse(result)


def _sniff_file_type(header: bytes) -> str:
    # Content-based detection (magic numbers) - never trust the
    # filename's extension for what a file actually is.
    if header.startswith(b"\xff\xd8\xff"):
        return "JPEG-bild"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG-bild"
    if header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
        return "GIF-bild"
    if header.startswith(b"BM"):
        return "BMP-bild"
    if header.startswith(b"II*\x00") or header.startswith(b"MM\x00*"):
        return "TIFF-bild"
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "WEBP-bild"
    if header[:4] == b"RIFF" and header[8:12] == b"AVI ":
        return "AVI-video"
    if header[4:8] == b"ftyp":
        return "MP4/QuickTime-video"
    if header.startswith(b"%PDF"):
        return "PDF-dokument"
    if header.startswith(b"MZ"):
        return "Windows-program/DLL (MZ)"
    if header.startswith(b"MSCF"):
        return "CAB-arkiv"
    if header.startswith(b"PK\x03\x04"):
        return "ZIP-arkiv"
    if header and all(32 <= b < 127 or b in (9, 10, 13) for b in header):
        return "Textfil"
    return "Okänd binärfil"


_EXPECTED_LABEL_FOR_EXT = {
    ".jpg": "JPEG-bild",
    ".jpeg": "JPEG-bild",
    ".png": "PNG-bild",
    ".gif": "GIF-bild",
    ".bmp": "BMP-bild",
    ".tif": "TIFF-bild",
    ".tiff": "TIFF-bild",
    ".webp": "WEBP-bild",
    ".avi": "AVI-video",
    ".mp4": "MP4/QuickTime-video",
    ".mov": "MP4/QuickTime-video",
    ".pdf": "PDF-dokument",
}


@app.get("/api/file-summary")
def file_summary(_: int = Depends(require_session)):
    total = 0
    category_counts: dict[str, int] = {}
    mismatches = []
    root = get_active_photos_root()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        total += 1
        with path.open("rb") as f:
            header = f.read(64)
        detected = _sniff_file_type(header)
        category_counts[detected] = category_counts.get(detected, 0) + 1

        ext = path.suffix.lower()
        expected = _EXPECTED_LABEL_FOR_EXT.get(ext)
        if expected and detected != expected:
            mismatches.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "extension": ext,
                    "detected": detected,
                }
            )

    categories = [
        {"label": label, "count": count}
        for label, count in sorted(category_counts.items(), key=lambda kv: -kv[1])
    ]
    return {"total_files": total, "categories": categories, "extension_mismatches": mismatches}


PLACEHOLDER_BG = {".pdf": (70, 70, 74), None: (40, 44, 52)}


def _truncate_to_width(draw, text: str, font, max_width: int) -> str:
    if draw.textlength(text, font=font) <= max_width:
        return text
    while text and draw.textlength(text + "…", font=font) > max_width:
        text = text[:-1]
    return text + "…"


def _draw_document_icon(draw, cx: int, top: int, size: int, accent) -> None:
    # Generic "document with folded corner" glyph - not any specific
    # vendor's file-type logo, just the universal document shape.
    fold = size // 4
    left, right = cx - size // 2, cx + size // 2
    bottom = top + size
    draw.polygon(
        [
            (left, top), (right - fold, top), (right, top + fold),
            (right, bottom), (left, bottom),
        ],
        fill="white", outline=(120, 120, 120),
    )
    draw.polygon([(right - fold, top), (right, top + fold), (right - fold, top + fold)], fill=(200, 200, 200))
    for i in range(3):
        y = top + fold + 14 + i * 12
        if y < bottom - 10:
            draw.line([(left + 12, y), (right - 12, y)], fill=accent, width=3)


def _draw_play_icon(draw, cx: int, cy: int, size: int) -> None:
    # Generic "play button" glyph (rounded frame + triangle) - the
    # universal video symbol, not any single app/vendor's mark.
    half = size // 2
    draw.rounded_rectangle(
        [cx - half, cy - half, cx + half, cy + half], radius=size // 6,
        outline="white", width=4,
    )
    t = size // 3
    draw.polygon(
        [(cx - t // 2, cy - t), (cx - t // 2, cy + t), (cx + t, cy)],
        fill="white",
    )


def _make_placeholder_thumb(cache_path: Path, filename: str, ext: str) -> None:
    from PIL import ImageFont

    bg = PLACEHOLDER_BG.get(ext, PLACEHOLDER_BG[None])
    im = Image.new("RGB", THUMB_SIZE, color=bg)
    draw = ImageDraw.Draw(im)
    cx = THUMB_SIZE[0] // 2
    icon_size = int(THUMB_SIZE[1] * 0.42)

    if ext in VIDEO_EXTS:
        _draw_play_icon(draw, cx, THUMB_SIZE[1] // 2 - 20, icon_size)
    else:
        _draw_document_icon(draw, cx, THUMB_SIZE[1] // 2 - icon_size // 2 - 20, icon_size, (180, 60, 60))

    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    label = _truncate_to_width(draw, filename, font, THUMB_SIZE[0] - 20)
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw / 2, THUMB_SIZE[1] - 44), label, fill="white", font=font)
    im.save(cache_path, "JPEG", quality=82)


@app.get("/thumb")
def thumb(p: str = Query(...), _: int = Depends(require_session)):
    src = resolve_relpath(p)
    ext = src.suffix.lower()
    cache_path = THUMB_CACHE / (p + ".jpg")
    if not cache_path.exists() or cache_path.stat().st_mtime < src.stat().st_mtime:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with _thumb_semaphore:
            picture_ok = False
            if ext in PICTURE_EXTS:
                try:
                    with Image.open(src) as im:
                        # Must run before exif_transpose/thumbnail() - both
                        # would otherwise force a full-resolution decode
                        # first. draft() only affects JPEG sources and is
                        # a best-effort hint (actual decode size may not
                        # match exactly), which is fine since .thumbnail()
                        # below still resizes precisely to THUMB_SIZE.
                        im.draft("RGB", THUMB_SIZE)
                        im = ImageOps.exif_transpose(im)
                        im.thumbnail(THUMB_SIZE)
                        if im.mode != "RGB":
                            im = im.convert("RGB")
                        im.save(cache_path, "JPEG", quality=82)
                    picture_ok = True
                except Exception:
                    picture_ok = False
            if not picture_ok:
                _make_placeholder_thumb(cache_path, src.name, ext)
    return FileResponse(cache_path, media_type="image/jpeg")


@app.get("/original")
def original(p: str = Query(...), _: int = Depends(require_session)):
    src = resolve_relpath(p)
    mime = mimetypes.guess_type(src.name)[0] or "application/octet-stream"
    return FileResponse(src, media_type=mime, filename=src.name)


async def _read_capped(upload: UploadFile, max_bytes: int) -> bytes:
    chunks = []
    total = 0
    while True:
        chunk = await upload.read(_UPLOAD_READ_CHUNK_BYTES)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(status_code=413, detail="file too large")
        chunks.append(chunk)
    return b"".join(chunks)


@app.post("/api/upload", status_code=201)
async def upload_photo(file: UploadFile = File(...), user_id: int = Depends(require_session)):
    # Any logged-in user, not admin-gated - dpfas_media is the shared
    # scratch space every account uploads their own pictures into, kept
    # apart from momfiles by name alone, never by who's allowed to write.
    ext = Path(file.filename or "").suffix.lower()
    if ext not in PICTURE_EXTS:
        raise HTTPException(status_code=400, detail="only picture uploads are supported")
    body = await _read_capped(file, MAX_PHOTO_UPLOAD_BYTES)
    # Content-hashed, not the client's original filename - never trust a
    # client-supplied filename as a path component, and this gets free
    # dedup if the same photo is uploaded twice by the same user.
    digest = hashlib.sha256(body).hexdigest()
    dest_dir = PHOTOS_LIBRARY_ROOT / UPLOAD_SOURCE_NAME / str(user_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"{digest}{ext}"
    dest_path.write_bytes(body)
    return {"path": dest_path.relative_to(PHOTOS_LIBRARY_ROOT / UPLOAD_SOURCE_NAME).as_posix()}


@app.post("/api/voiceover")
async def upload_voiceover(
    request: Request,
    events: str = Form(...),
    audio: UploadFile = File(...),
    _: int = Depends(require_session),
):
    try:
        parsed_events = json.loads(events)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid events json")
    filename = f"{uuid.uuid4().hex}.webm"
    dest = STORY_DIR / filename
    with dest.open("wb") as f:
        f.write(await audio.read())
    with _db_lock:
        db.execute(
            "INSERT INTO voiceovers (ts, audio_filename, events_json, client_ip) VALUES (?, ?, ?, ?)",
            (
                datetime.now(timezone.utc).isoformat(),
                filename,
                json.dumps(parsed_events),
                request.client.host if request.client else None,
            ),
        )
        db.commit()
    return {"ok": True}


@app.get("/api/voiceovers")
def list_voiceovers(_: int = Depends(require_session)):
    with _db_lock:
        rows = db.execute(
            "SELECT id, ts, audio_filename, events_json FROM voiceovers ORDER BY id DESC"
        ).fetchall()
    result = []
    for row_id, ts, audio_filename, events_json in rows:
        try:
            parsed_events = json.loads(events_json)
        except ValueError:
            parsed_events = []
        paths_in_order = []
        for ev in parsed_events:
            if ev.get("path") and ev["path"] not in paths_in_order:
                paths_in_order.append(ev["path"])
        result.append(
            {
                "id": row_id,
                "ts": ts,
                "audio_url": f"/voiceover-audio/{audio_filename}",
                "image_count": len(paths_in_order),
                "first_image": paths_in_order[0] if paths_in_order else None,
            }
        )
    return result


@app.get("/api/voiceover/{voiceover_id}")
def get_voiceover(voiceover_id: int, _: int = Depends(require_session)):
    with _db_lock:
        row = db.execute(
            "SELECT id, ts, audio_filename, events_json FROM voiceovers WHERE id = ?", (voiceover_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    row_id, ts, audio_filename, events_json = row
    try:
        parsed_events = json.loads(events_json)
    except ValueError:
        parsed_events = []
    return {"id": row_id, "ts": ts, "audio_url": f"/voiceover-audio/{audio_filename}", "events": parsed_events}


@app.get("/voiceover-audio/{filename}")
def voiceover_audio(filename: str, _: int = Depends(require_session)):
    if "/" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="invalid filename")
    path = STORY_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(path, media_type="audio/webm")


@app.get("/", include_in_schema=False)
def index(request: Request):
    # Gate the app shell itself, not just the API - otherwise an
    # unauthenticated visitor sees the full working-looking UI before the
    # first data fetch discovers there's no session and redirects. See
    # documentation/bugs/repo/fixed/2026-07-17-unauthenticated-static-shell-before-login.md
    if not has_valid_session(request):
        return RedirectResponse(url="/login")
    return FileResponse(Path(__file__).parent / "static" / "index.html")


app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
