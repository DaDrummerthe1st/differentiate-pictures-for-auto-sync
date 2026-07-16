import json
import mimetypes
import sqlite3
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps
from pydantic import BaseModel
from starlette.background import BackgroundTask

PHOTOS_ROOT = Path("/photos").resolve()
THUMB_CACHE = Path("/thumbcache")
THUMB_CACHE.mkdir(parents=True, exist_ok=True)

ZIP_CACHE = Path("/zipcache")
ZIP_CACHE.mkdir(parents=True, exist_ok=True)

STORY_DIR = Path("/stories")
STORY_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp"}
THUMB_SIZE = (340, 340)

DB_PATH = Path("/data/analytics.db")
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

app = FastAPI()


class Event(BaseModel):
    type: str
    detail: str = ""


@app.post("/api/event")
def log_event(event: Event, request: Request):
    db.execute(
        "INSERT INTO events (ts, event_type, detail, client_ip) VALUES (?, ?, ?, ?)",
        (
            datetime.now(timezone.utc).isoformat(),
            event.type,
            event.detail,
            request.client.host if request.client else None,
        ),
    )
    db.commit()
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
def api_tree():
    headlines: dict[str, dict[str, list[str]]] = {}

    for path in PHOTOS_ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
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


@app.get("/thumb")
def thumb(p: str = Query(...)):
    src = resolve_relpath(p)
    cache_path = THUMB_CACHE / (p + ".jpg")
    if not cache_path.exists() or cache_path.stat().st_mtime < src.stat().st_mtime:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im)
            im.thumbnail(THUMB_SIZE)
            if im.mode != "RGB":
                im = im.convert("RGB")
            im.save(cache_path, "JPEG", quality=82)
    return FileResponse(cache_path, media_type="image/jpeg")


@app.get("/original")
def original(p: str = Query(...)):
    src = resolve_relpath(p)
    mime = mimetypes.guess_type(src.name)[0] or "application/octet-stream"
    return FileResponse(src, media_type=mime, filename=src.name)


class ZipRequest(BaseModel):
    paths: list[str]


@app.post("/api/zip")
def zip_paths(req: ZipRequest):
    if not req.paths:
        raise HTTPException(status_code=400, detail="no paths given")
    zip_path = ZIP_CACHE / f"{uuid.uuid4().hex}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zf:
        for p in req.paths:
            src = resolve_relpath(p)
            zf.write(src, arcname=src.relative_to(PHOTOS_ROOT).as_posix())
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="mammas_bilder.zip",
        background=BackgroundTask(zip_path.unlink, missing_ok=True),
    )


@app.post("/api/voiceover")
async def upload_voiceover(request: Request, events: str = Form(...), audio: UploadFile = File(...)):
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
def list_voiceovers():
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
def get_voiceover(voiceover_id: int):
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
def voiceover_audio(filename: str):
    if "/" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="invalid filename")
    path = STORY_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(path, media_type="audio/webm")


app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
