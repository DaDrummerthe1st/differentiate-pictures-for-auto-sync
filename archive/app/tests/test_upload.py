import io
import os
import time

import jwt
from PIL import Image

from app import main as app_main
from app.auth import ACCESS_COOKIE

_SECRET = os.environ["JWT_SECRET_KEY"]


def _token(sub: str = "7", username: str = "opaqueuser7") -> str:
    now = int(time.time())
    payload = {
        "sub": sub,
        "username": username,
        "type": "access",
        "iat": now,
        "exp": now + 900,
        "jti": f"jti-upload-{sub}",
    }
    return jwt.encode(payload, _SECRET, algorithm="HS256")


def _jpeg_bytes(color: str = "red") -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (20, 15), color=color).save(buf, "JPEG")
    return buf.getvalue()


def test_upload_requires_a_session(client):
    client.cookies.delete(ACCESS_COOKIE)
    res = client.post("/api/upload", files={"file": ("pic.jpg", _jpeg_bytes(), "image/jpeg")})
    assert res.status_code == 401


def test_upload_lands_under_dpfas_media_in_a_per_username_subdirectory(client):
    client.cookies.set(ACCESS_COOKIE, _token(username="opaqueuser7"))
    res = client.post("/api/upload", files={"file": ("holiday.jpg", _jpeg_bytes(), "image/jpeg")})

    assert res.status_code == 201
    path = res.json()["path"]
    assert (app_main.PHOTOS_LIBRARY_ROOT / app_main.MEDIA_ROOT_NAME / "opaqueuser7" / path).is_file()


def test_upload_does_not_use_the_original_filename(client):
    client.cookies.set(ACCESS_COOKIE, _token(username="opaqueuser7"))
    res = client.post("/api/upload", files={"file": ("my_original_name.jpg", _jpeg_bytes(), "image/jpeg")})

    path = res.json()["path"]
    assert "my_original_name" not in path
    # sha256 hex digest + extension, not a uuid, not the client's name
    stem = path.rsplit(".", 1)[0]
    assert len(stem) == 64
    int(stem, 16)  # raises ValueError if it isn't real hex


def test_upload_rejects_a_non_picture_extension(client):
    client.cookies.set(ACCESS_COOKIE, _token(username="opaqueuser7"))
    res = client.post("/api/upload", files={"file": ("notes.txt", b"just text", "text/plain")})
    assert res.status_code == 400


def test_upload_rejects_an_oversized_file(client, monkeypatch):
    monkeypatch.setattr(app_main, "MAX_PHOTO_UPLOAD_BYTES", 10)
    client.cookies.set(ACCESS_COOKIE, _token(username="opaqueuser7"))
    res = client.post("/api/upload", files={"file": ("big.jpg", _jpeg_bytes(), "image/jpeg")})
    assert res.status_code == 413


def test_uploading_identical_bytes_twice_does_not_error(client):
    client.cookies.set(ACCESS_COOKIE, _token(username="opaqueuser7"))
    body = _jpeg_bytes()
    first = client.post("/api/upload", files={"file": ("a.jpg", body, "image/jpeg")})
    second = client.post("/api/upload", files={"file": ("b.jpg", body, "image/jpeg")})

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["path"] == second.json()["path"]


def test_uploaded_photo_becomes_visible_via_api_tree(client):
    # Regression test for the 2026-08-08 "uploaded picture doesn't show up
    # in the gallery" report - root-caused to a frontend feedback gap, not
    # a backend visibility bug, but nothing previously asserted the tree
    # endpoint actually reflects an upload, so that class of regression
    # could still slip through unnoticed.
    client.cookies.set(ACCESS_COOKIE, _token(username="opaqueuser7"))
    upload_res = client.post("/api/upload", files={"file": ("holiday.jpg", _jpeg_bytes(), "image/jpeg")})
    assert upload_res.status_code == 201
    path = upload_res.json()["path"]

    tree = client.get("/api/tree").json()
    all_images = [img for section in tree for chunk in section["chunks"] for img in chunk["images"]]
    assert path in all_images


def test_upload_is_not_visible_in_another_users_tree(client):
    client.cookies.set(ACCESS_COOKIE, _token(username="opaqueuser7"))
    upload_res = client.post("/api/upload", files={"file": ("holiday.jpg", _jpeg_bytes(), "image/jpeg")})
    path = upload_res.json()["path"]

    client.cookies.set(ACCESS_COOKIE, _token(username="someoneelse"))
    tree = client.get("/api/tree").json()
    all_images = [img for section in tree for chunk in section["chunks"] for img in chunk["images"]]
    assert path not in all_images
