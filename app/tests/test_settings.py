import os
import time

import jwt
import pytest

from app import main as app_main
from app.main import db as _db

_SECRET = os.environ["JWT_SECRET_KEY"]


def _token(sub: str = "1", role: str = "member") -> str:
    now = int(time.time())
    payload = {
        "sub": sub,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + 900,
        "jti": f"jti-settings-{sub}-{role}",
    }
    return jwt.encode(payload, _SECRET, algorithm="HS256")


def _as_user(client, sub: str, role: str = "member"):
    client.cookies.set("photo_server_access", _token(sub, role))
    return client


@pytest.fixture()
def sources_root(tmp_path, monkeypatch):
    """A fresh PHOTOS_LIBRARY_ROOT with two real subdirectories, isolated
    from the global conftest fixture tree - lets `available` assertions be
    exact instead of coupled to whatever else conftest.py sets up."""
    (tmp_path / "dpfas_media").mkdir()
    (tmp_path / "momfiles").mkdir()
    monkeypatch.setattr(app_main, "PHOTOS_LIBRARY_ROOT", tmp_path)

    def _set_active(name: str) -> None:
        _db.execute(
            "INSERT INTO app_settings (id, active_source, updated_at) VALUES (1, ?, 'test-setup') "
            "ON CONFLICT(id) DO UPDATE SET active_source = excluded.active_source, updated_at = excluded.updated_at",
            (name,),
        )
        _db.commit()

    _set_active("dpfas_media")
    try:
        yield tmp_path
    finally:
        # The app's sqlite connection is a module-level singleton shared
        # across the whole test session (see conftest.py) - a test here
        # that PUTs a different active_source would otherwise leak into
        # every later test file, pointing get_active_photos_root() at a
        # tmp_path subdirectory this fixture already tore down.
        _set_active("dpfas_media")


def test_member_get_photos_source_is_forbidden(client, sources_root):
    _as_user(client, "2", role="member")
    res = client.get("/api/settings/photos-source")
    assert res.status_code == 403


def test_member_put_photos_source_is_forbidden(client, sources_root):
    _as_user(client, "2", role="member")
    res = client.put("/api/settings/photos-source", json={"active": "momfiles"})
    assert res.status_code == 403
    assert app_main._get_active_source() == "dpfas_media"


def test_admin_get_photos_source_lists_real_subdirectories(client, sources_root):
    _as_user(client, "1", role="admin")
    res = client.get("/api/settings/photos-source")
    assert res.status_code == 200
    data = res.json()
    assert data["active"] == "dpfas_media"
    assert data["available"] == ["dpfas_media", "momfiles"]


def test_admin_put_unknown_source_is_rejected(client, sources_root):
    _as_user(client, "1", role="admin")
    res = client.put("/api/settings/photos-source", json={"active": "not-a-real-dir"})
    assert res.status_code == 400
    assert app_main._get_active_source() == "dpfas_media"


def test_admin_put_known_source_persists_and_reflects_in_get(client, sources_root):
    _as_user(client, "1", role="admin")
    put_res = client.put("/api/settings/photos-source", json={"active": "momfiles"})
    assert put_res.status_code == 200
    assert put_res.json()["active"] == "momfiles"

    get_res = client.get("/api/settings/photos-source")
    assert get_res.json()["active"] == "momfiles"


def test_switching_source_changes_tree_and_file_summary_contents(client, sources_root):
    (sources_root / "dpfas_media" / "only_in_dpfas.jpg").write_bytes(b"\xff\xd8\xff" + b"\x00" * 20)
    (sources_root / "momfiles" / "only_in_momfiles.jpg").write_bytes(b"\xff\xd8\xff" + b"\x00" * 20)
    _as_user(client, "1", role="admin")

    tree_before = client.get("/api/tree").json()
    paths_before = {img for section in tree_before for chunk in section["chunks"] for img in chunk["images"]}
    assert "only_in_dpfas.jpg" in paths_before
    assert "only_in_momfiles.jpg" not in paths_before

    client.put("/api/settings/photos-source", json={"active": "momfiles"})

    tree_after = client.get("/api/tree").json()
    paths_after = {img for section in tree_after for chunk in section["chunks"] for img in chunk["images"]}
    assert "only_in_momfiles.jpg" in paths_after
    assert "only_in_dpfas.jpg" not in paths_after

    summary_after = client.get("/api/file-summary").json()
    assert summary_after["total_files"] == 1
