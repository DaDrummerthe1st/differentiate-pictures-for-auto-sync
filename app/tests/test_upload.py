import io
import os
import time

import jwt
from PIL import Image

from app import main as app_main
from app.auth import ACCESS_COOKIE

_SECRET = os.environ["JWT_SECRET_KEY"]


def _token(sub: str = "7") -> str:
    now = int(time.time())
    payload = {
        "sub": sub,
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


def test_upload_lands_under_dpfas_media_in_a_per_user_subdirectory(client):
    client.cookies.set(ACCESS_COOKIE, _token(sub="7"))
    res = client.post("/api/upload", files={"file": ("holiday.jpg", _jpeg_bytes(), "image/jpeg")})

    assert res.status_code == 201
    path = res.json()["path"]
    assert path.startswith("7/")
    assert (app_main.PHOTOS_LIBRARY_ROOT / app_main.UPLOAD_SOURCE_NAME / path).is_file()


def test_upload_does_not_use_the_original_filename(client):
    client.cookies.set(ACCESS_COOKIE, _token(sub="7"))
    res = client.post("/api/upload", files={"file": ("my_original_name.jpg", _jpeg_bytes(), "image/jpeg")})

    path = res.json()["path"]
    assert "my_original_name" not in path
    # sha256 hex digest + extension, not a uuid, not the client's name
    stem = path.split("/")[-1].rsplit(".", 1)[0]
    assert len(stem) == 64
    int(stem, 16)  # raises ValueError if it isn't real hex


def test_upload_rejects_a_non_picture_extension(client):
    client.cookies.set(ACCESS_COOKIE, _token(sub="7"))
    res = client.post("/api/upload", files={"file": ("notes.txt", b"just text", "text/plain")})
    assert res.status_code == 400


def test_upload_rejects_an_oversized_file(client, monkeypatch):
    monkeypatch.setattr(app_main, "MAX_PHOTO_UPLOAD_BYTES", 10)
    client.cookies.set(ACCESS_COOKIE, _token(sub="7"))
    res = client.post("/api/upload", files={"file": ("big.jpg", _jpeg_bytes(), "image/jpeg")})
    assert res.status_code == 413


def test_uploading_identical_bytes_twice_does_not_error(client):
    client.cookies.set(ACCESS_COOKIE, _token(sub="7"))
    body = _jpeg_bytes()
    first = client.post("/api/upload", files={"file": ("a.jpg", body, "image/jpeg")})
    second = client.post("/api/upload", files={"file": ("b.jpg", body, "image/jpeg")})

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["path"] == second.json()["path"]


def test_upload_always_lands_in_dpfas_media_even_if_a_different_source_is_active(client, tmp_path, monkeypatch):
    # Safety guard: an admin switching the served (active) source to
    # momfiles must never redirect uploads there too - uploads always go
    # to dpfas_media by name, independent of app_settings.active_source.
    (tmp_path / "dpfas_media").mkdir()
    (tmp_path / "momfiles").mkdir()
    monkeypatch.setattr(app_main, "PHOTOS_LIBRARY_ROOT", tmp_path)
    app_main.db.execute(
        "INSERT INTO app_settings (id, active_source, updated_at) VALUES (1, 'momfiles', 'test-setup') "
        "ON CONFLICT(id) DO UPDATE SET active_source = excluded.active_source, updated_at = excluded.updated_at"
    )
    app_main.db.commit()
    try:
        client.cookies.set(ACCESS_COOKIE, _token(sub="7"))
        res = client.post("/api/upload", files={"file": ("pic.jpg", _jpeg_bytes(), "image/jpeg")})

        assert res.status_code == 201
        assert not any((tmp_path / "momfiles").rglob("*.jpg"))
        assert list((tmp_path / "dpfas_media" / "7").glob("*.jpg"))
    finally:
        app_main.db.execute(
            "INSERT INTO app_settings (id, active_source, updated_at) VALUES (1, 'dpfas_media', 'test-teardown') "
            "ON CONFLICT(id) DO UPDATE SET active_source = excluded.active_source, updated_at = excluded.updated_at"
        )
        app_main.db.commit()
