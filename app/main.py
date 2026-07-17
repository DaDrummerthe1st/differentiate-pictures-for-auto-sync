import json
import mimetypes
import os
import sqlite3
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageDraw, ImageOps
from pydantic import BaseModel

from app.auth import load_auth_config, require_session

load_auth_config()

PHOTOS_ROOT = Path(os.environ.get("PHOTOS_ROOT", "/photos")).resolve()
THUMB_CACHE = Path(os.environ.get("THUMB_CACHE_DIR", "/thumbcache"))
THUMB_CACHE.mkdir(parents=True, exist_ok=True)

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
db.commit()


def _log_event(event_type: str, detail: str = "", client_ip: str | None = None) -> None:
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


app = FastAPI(lifespan=lifespan)


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


def resolve_relpath(relpath: str) -> Path:
    candidate = (PHOTOS_ROOT / relpath).resolve()
    if PHOTOS_ROOT not in candidate.parents and candidate != PHOTOS_ROOT:
        raise HTTPException(status_code=400, detail="invalid path")
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return candidate


@app.get("/api/tree")
def api_tree(_: int = Depends(require_session)):
    headlines: dict[str, dict[str, list[str]]] = {}

    for path in PHOTOS_ROOT.rglob("*"):
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
        rel = path.relative_to(PHOTOS_ROOT)
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
    for path in sorted(PHOTOS_ROOT.rglob("*")):
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
                    "path": path.relative_to(PHOTOS_ROOT).as_posix(),
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
        picture_ok = False
        if ext in PICTURE_EXTS:
            try:
                with Image.open(src) as im:
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


app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
