"""Standalone pictures register: walks a folder (a local directory today, an
sshfs-mounted NAS share tomorrow, or any other source) and maintains a
central SQLite metadata register of every valid picture file found, so
photos ingested from many disparate sources over time land in one place
instead of being tied to whichever folder happened to be scanned first.
Self-contained - no dependency on detector/, app/, or any other existing
code in this repo, same pattern as modules/quality.py and modules/objects.py.

Schema (documentation/data-modeling/PICTURES_PIPELINE.md):
- `pictures`: one row per unique photo, keyed by MD5 - the same photo found
  again at a different path (moved, re-mounted, copied to a second drive)
  stays one picture.
- `locations`: one row per place a picture has been found - path, an
  optional source label (e.g. "nas_pechakucha"), and per-location
  file_metadata (filesystem stat data, which is inherently per-location:
  the same photo can have different mtimes/inodes at different paths).

Rescans are incremental: a path already registered with unchanged size/mtime
is skipped without re-hashing; a changed path is re-hashed and, if its
content changed, repointed at the right picture (creating one if needed).

Usage: python3 -m modules.pictures <folder-path> [source-label]
"""
import ctypes
import hashlib
import json
import os
import sqlite3
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from PIL import Image, UnidentifiedImageError

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "databases", "pictures.db"
)

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".bmp", ".tif", ".tiff", ".webp", ".gif"}

_HASH_CHUNK_SIZE = 1024 * 1024

# statx(2) - the only way to get a true filesystem creation time on Linux;
# Python's os.stat() never exposes st_birthtime there (only macOS/BSD do).
_STATX_BTIME = 0x00000800
_AT_FDCWD = -100
_AT_STATX_SYNC_AS_STAT = 0x00000000


class _StatxTimestamp(ctypes.Structure):
    _fields_ = [
        ("tv_sec", ctypes.c_int64),
        ("tv_nsec", ctypes.c_uint32),
        ("__reserved", ctypes.c_int32),
    ]


class _Statx(ctypes.Structure):
    _fields_ = [
        ("stx_mask", ctypes.c_uint32),
        ("stx_blksize", ctypes.c_uint32),
        ("stx_attributes", ctypes.c_uint64),
        ("stx_nlink", ctypes.c_uint32),
        ("stx_uid", ctypes.c_uint32),
        ("stx_gid", ctypes.c_uint32),
        ("stx_mode", ctypes.c_uint16),
        ("__spare0", ctypes.c_uint16 * 1),
        ("stx_ino", ctypes.c_uint64),
        ("stx_size", ctypes.c_uint64),
        ("stx_blocks", ctypes.c_uint64),
        ("stx_attributes_mask", ctypes.c_uint64),
        ("stx_atime", _StatxTimestamp),
        ("stx_btime", _StatxTimestamp),
        ("stx_ctime", _StatxTimestamp),
        ("stx_mtime", _StatxTimestamp),
        ("stx_rdev_major", ctypes.c_uint32),
        ("stx_rdev_minor", ctypes.c_uint32),
        ("stx_dev_major", ctypes.c_uint32),
        ("stx_dev_minor", ctypes.c_uint32),
        ("stx_mnt_id", ctypes.c_uint64),
        ("stx_dio_mem_align", ctypes.c_uint32),
        ("stx_dio_offset_align", ctypes.c_uint32),
        ("__spare3", ctypes.c_uint64 * 12),
    ]


def _statx_birth_time(path: str) -> tuple[float | None, bool]:
    """(birth_time, available) via statx(2)'s STATX_BTIME field. Falls back
    to (None, False) - never guessed from mtime/ctime - on any
    platform/kernel/filesystem/mount that doesn't support it (older
    kernels, glibc < 2.28, many network filesystems including sshfs)."""
    try:
        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        buf = _Statx()
        result = libc.statx(
            _AT_FDCWD,
            os.fsencode(path),
            _AT_STATX_SYNC_AS_STAT,
            _STATX_BTIME,
            ctypes.byref(buf),
        )
        if result != 0 or not (buf.stx_mask & _STATX_BTIME):
            return None, False
        return float(buf.stx_btime.tv_sec) + buf.stx_btime.tv_nsec / 1e9, True
    except OSError:
        return None, False


def _is_valid_picture_file(path: str) -> bool:
    if os.path.splitext(path)[1].lower() not in VALID_EXTENSIONS:
        return False
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except (UnidentifiedImageError, OSError):
        return False


def _md5(path: str) -> str:
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(_HASH_CHUNK_SIZE), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _file_metadata(path: str) -> dict:
    stat_result = os.stat(path)
    birth_time, birth_time_available = _statx_birth_time(path)
    return {
        "filename": os.path.basename(path),
        "size": stat_result.st_size,
        "mode": stat_result.st_mode,
        "mtime": stat_result.st_mtime,
        "ctime": stat_result.st_ctime,
        "birth_time": birth_time,
        "birth_time_available": birth_time_available,
    }


@dataclass(frozen=True)
class PictureLocation:
    picture_id: str
    location_id: str
    path: str
    md5: str
    source: str | None
    file_metadata: dict


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pictures (
            id TEXT PRIMARY KEY,
            md5 TEXT NOT NULL UNIQUE,
            first_registered_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS locations (
            id TEXT PRIMARY KEY,
            picture_id TEXT NOT NULL REFERENCES pictures(id),
            path TEXT NOT NULL UNIQUE,
            source TEXT,
            file_metadata TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL
        )
        """
    )


def _find_or_create_picture(conn: sqlite3.Connection, md5: str, now: str) -> str:
    row = conn.execute("SELECT id FROM pictures WHERE md5 = ?", (md5,)).fetchone()
    if row is not None:
        return row["id"]
    picture_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO pictures (id, md5, first_registered_at) VALUES (?, ?, ?)",
        (picture_id, md5, now),
    )
    return picture_id


def _register_file(conn: sqlite3.Connection, path: str, source: str | None, now: str) -> PictureLocation:
    metadata = _file_metadata(path)
    existing = conn.execute(
        """
        SELECT locations.id AS location_id, locations.picture_id, locations.file_metadata,
               pictures.md5
        FROM locations JOIN pictures ON pictures.id = locations.picture_id
        WHERE locations.path = ?
        """,
        (path,),
    ).fetchone()

    if existing is not None:
        old_metadata = json.loads(existing["file_metadata"])
        if old_metadata.get("size") == metadata["size"] and old_metadata.get("mtime") == metadata["mtime"]:
            conn.execute("UPDATE locations SET last_seen_at = ? WHERE id = ?", (now, existing["location_id"]))
            return PictureLocation(
                picture_id=existing["picture_id"],
                location_id=existing["location_id"],
                path=path,
                md5=existing["md5"],
                source=source,
                file_metadata=old_metadata,
            )

    md5 = _md5(path)
    picture_id = _find_or_create_picture(conn, md5, now)
    metadata_json = json.dumps(metadata)

    if existing is not None:
        conn.execute(
            "UPDATE locations SET picture_id = ?, source = ?, file_metadata = ?, last_seen_at = ? WHERE id = ?",
            (picture_id, source, metadata_json, now, existing["location_id"]),
        )
        location_id = existing["location_id"]
    else:
        location_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO locations (id, picture_id, path, source, file_metadata, first_seen_at, last_seen_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (location_id, picture_id, path, source, metadata_json, now, now),
        )

    return PictureLocation(
        picture_id=picture_id,
        location_id=location_id,
        path=path,
        md5=md5,
        source=source,
        file_metadata=metadata,
    )


def GetListOfValidPictureFiles(
    folder_path: str, source: str | None = None, db_path: str = DEFAULT_DB_PATH
) -> list[PictureLocation]:
    """Walk folder_path (recursively), register every valid picture file
    into the pictures/locations tables at db_path, and return one
    PictureLocation per valid picture file found this call."""
    conn = _connect(db_path)
    try:
        _init_db(conn)
        now = _now()
        results = [
            _register_file(conn, os.path.join(root, filename), source, now)
            for root, _dirs, files in os.walk(folder_path)
            for filename in files
            if _is_valid_picture_file(os.path.join(root, filename))
        ]
        conn.commit()
        return results
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 -m modules.pictures <folder-path> [source-label]", file=sys.stderr)
        sys.exit(1)
    folder = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else None
    found = GetListOfValidPictureFiles(folder, source=label)
    print(f"Registered {len(found)} picture file(s) from {folder} into {DEFAULT_DB_PATH}:")
    for entry in found:
        print(f"  {entry.path}  (picture_id={entry.picture_id}, md5={entry.md5})")
