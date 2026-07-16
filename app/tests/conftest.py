import os
import tempfile
from pathlib import Path

import pytest
from PIL import Image

_TEST_ROOT = Path(tempfile.mkdtemp(prefix="mpv-test-"))
PHOTOS_ROOT = _TEST_ROOT / "photos"
PHOTOS_ROOT.mkdir()

os.environ["PHOTOS_ROOT"] = str(PHOTOS_ROOT)
os.environ["THUMB_CACHE_DIR"] = str(_TEST_ROOT / "thumbcache")
os.environ["ZIP_CACHE_DIR"] = str(_TEST_ROOT / "zipcache")
os.environ["STORY_DIR"] = str(_TEST_ROOT / "stories")
os.environ["ANALYTICS_DB_PATH"] = str(_TEST_ROOT / "data" / "analytics.db")

(PHOTOS_ROOT / "AlbumA" / "1").mkdir(parents=True)
(PHOTOS_ROOT / "AlbumA" / "2").mkdir(parents=True)


def _make_image(path: Path, color: str) -> None:
    Image.new("RGB", (40, 30), color=color).save(path, "JPEG")


_make_image(PHOTOS_ROOT / "AlbumA" / "1" / "pic1.jpg", "red")
_make_image(PHOTOS_ROOT / "AlbumA" / "1" / "pic2.jpg", "green")
_make_image(PHOTOS_ROOT / "AlbumA" / "2" / "pic3.jpg", "blue")
(PHOTOS_ROOT / "AlbumA" / "junk.exe").write_bytes(b"not an image")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app, ZIP_CACHE  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def zip_cache_dir() -> Path:
    return ZIP_CACHE
