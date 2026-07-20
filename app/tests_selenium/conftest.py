import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import jwt
import pytest
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Real browser tests against a real running uvicorn process - see
# scripts/test_selenium.sh (must be "up" before running this suite) and
# documentation/gui/TODO.md's Selenium decision. Separate from
# app/tests/conftest.py's TestClient-based fixture: that one exercises
# the app in-process and can't drive an actual browser/DOM.
_JWT_SECRET = "test-selenium-jwt-secret-key-at-least-32-chars"
_SELENIUM_URL = "http://127.0.0.1:4444/wd/hub"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _make_image(path: Path, color: str) -> None:
    Image.new("RGB", (40, 30), color=color).save(path, "JPEG")


def _valid_access_token() -> str:
    now = int(time.time())
    payload = {"sub": "1", "type": "access", "iat": now, "exp": now + 900, "jti": "selenium-jti"}
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


@pytest.fixture(scope="module")
def app_server():
    root = Path(tempfile.mkdtemp(prefix="mpv-selenium-"))
    photos_root = root / "photos"
    for album in ("AlbumA", "AlbumB", "AlbumC"):
        (photos_root / album).mkdir(parents=True)
    # AlbumA gets enough images to make the page taller than the test
    # window, so scroll-position tests have something to scroll through.
    for i in range(24):
        _make_image(photos_root / "AlbumA" / f"a{i}.jpg", "red")
    _make_image(photos_root / "AlbumB" / "b1.jpg", "green")
    _make_image(photos_root / "AlbumC" / "c1.jpg", "blue")

    port = _free_port()
    env = {
        **os.environ,
        "PHOTOS_ROOT": str(photos_root),
        "THUMB_CACHE_DIR": str(root / "thumbcache"),
        "STORY_DIR": str(root / "stories"),
        "ANALYTICS_DB_PATH": str(root / "data" / "analytics.db"),
        "JWT_SECRET_KEY": _JWT_SECRET,
    }
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=Path(__file__).resolve().parents[2],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    base_url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 15
    up = False
    while time.time() < deadline:
        try:
            urllib.request.urlopen(base_url + "/", timeout=1)
            up = True
            break
        except (urllib.error.URLError, ConnectionError):
            if proc.poll() is not None:
                break
            time.sleep(0.3)
    if not up:
        proc.terminate()
        proc.wait(timeout=5)
        out = proc.stdout.read().decode(errors="replace") if proc.stdout else ""
        raise RuntimeError(f"app server did not come up on {base_url}\n{out}")

    yield base_url

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture()
def driver(app_server):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1024,700")
    d = webdriver.Remote(command_executor=_SELENIUM_URL, options=options)
    try:
        # A cookie can only be added once the browser is already on the
        # target origin (any path) - the static shell needs no session,
        # so a first load of "/" is enough before injecting it.
        d.get(app_server + "/")
        d.add_cookie({"name": "photo_server_access", "value": _valid_access_token(), "path": "/"})
        d.get(app_server + "/")
        yield d
    finally:
        d.quit()
