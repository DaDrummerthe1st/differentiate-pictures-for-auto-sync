import os
import tempfile
import time
from pathlib import Path

import jwt
import pytest
from PIL import Image

_TEST_ROOT = Path(tempfile.mkdtemp(prefix="mpv-test-"))
PHOTOS_ROOT = _TEST_ROOT / "photos"
PHOTOS_ROOT.mkdir()

os.environ["PHOTOS_ROOT"] = str(PHOTOS_ROOT)
os.environ["THUMB_CACHE_DIR"] = str(_TEST_ROOT / "thumbcache")
os.environ["STORY_DIR"] = str(_TEST_ROOT / "stories")
os.environ["ANALYTICS_DB_PATH"] = str(_TEST_ROOT / "data" / "analytics.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-at-least-32-chars")

(PHOTOS_ROOT / "AlbumA" / "1").mkdir(parents=True)
(PHOTOS_ROOT / "AlbumA" / "2").mkdir(parents=True)


def _make_image(path: Path, color: str) -> None:
    Image.new("RGB", (40, 30), color=color).save(path, "JPEG")


_make_image(PHOTOS_ROOT / "AlbumA" / "1" / "pic1.jpg", "red")
_make_image(PHOTOS_ROOT / "AlbumA" / "1" / "pic2.jpg", "green")
_make_image(PHOTOS_ROOT / "AlbumA" / "2" / "pic3.jpg", "blue")
(PHOTOS_ROOT / "AlbumA" / "junk.exe").write_bytes(b"MZ" + b"\x00" * 30)
(PHOTOS_ROOT / "AlbumA" / "junk.dll").write_bytes(b"MZ" + b"\x00" * 30)
(PHOTOS_ROOT / "AlbumA" / "1" / "clip.avi").write_bytes(b"RIFF\x00\x00\x00\x00AVI ")
(PHOTOS_ROOT / "AlbumA" / "1" / "doc.pdf").write_bytes(b"%PDF-1.4 fake-pdf-bytes")
(PHOTOS_ROOT / "AlbumA" / "1" / "other_report.pdf").write_bytes(b"%PDF-1.4 other-fake-pdf-bytes")
(PHOTOS_ROOT / "AlbumA" / "notes.txt").write_bytes(b"just some plain text notes\n")
# Deliberately mismatched: a .jpg extension whose content is plain text,
# not a real JPEG - proves the summary sniffs actual bytes rather than
# trusting the filename.
(PHOTOS_ROOT / "AlbumA" / "fake_photo.jpg").write_bytes(b"this is not really a jpeg")

from fastapi.testclient import TestClient  # noqa: E402

from app.auth import ACCESS_COOKIE  # noqa: E402
from app.main import app  # noqa: E402


def _valid_access_token() -> str:
    now = int(time.time())
    payload = {"sub": "1", "type": "access", "iat": now, "exp": now + 900, "jti": "conftest-jti"}
    return jwt.encode(payload, os.environ["JWT_SECRET_KEY"], algorithm="HS256")


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        # Feature tests exercise app behavior, not the auth gate itself
        # (that's app/tests/test_auth_gate.py) - carry a valid session by
        # default so they don't all need to know about cookies.
        test_client.cookies.set(ACCESS_COOKIE, _valid_access_token())
        yield test_client
