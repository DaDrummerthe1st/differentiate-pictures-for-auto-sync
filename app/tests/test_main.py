import sqlite3

from app.main import DB_PATH


def _db():
    return sqlite3.connect(DB_PATH)


def test_tree_groups_by_headline_and_immediate_parent_chunk(client):
    res = client.get("/api/tree")
    assert res.status_code == 200
    sections = res.json()
    assert len(sections) == 1
    section = sections[0]
    assert section["headline"] == "AlbumA"
    chunks = {c["path"]: c["images"] for c in section["chunks"]}
    assert chunks["AlbumA/1"] == ["AlbumA/1/pic1.jpg", "AlbumA/1/pic2.jpg"]
    assert chunks["AlbumA/2"] == ["AlbumA/2/pic3.jpg"]


def test_tree_excludes_non_image_files(client):
    res = client.get("/api/tree")
    all_images = [img for h in res.json() for c in h["chunks"] for img in c["images"]]
    assert not any(img.endswith(".exe") for img in all_images)


def test_thumb_generates_jpeg(client):
    res = client.get("/thumb", params={"p": "AlbumA/1/pic1.jpg"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/jpeg"
    assert len(res.content) > 0


def test_thumb_rejects_path_traversal(client):
    res = client.get("/thumb", params={"p": "../../../../etc/passwd"})
    assert res.status_code == 400


def test_thumb_404_for_missing_file(client):
    res = client.get("/thumb", params={"p": "AlbumA/1/does_not_exist.jpg"})
    assert res.status_code == 404


def test_original_serves_file(client):
    res = client.get("/original", params={"p": "AlbumA/1/pic1.jpg"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/jpeg"


def test_original_rejects_path_traversal(client):
    res = client.get("/original", params={"p": "../../../../etc/passwd"})
    assert res.status_code == 400


def test_zip_endpoint_400_for_no_paths(client):
    res = client.post("/api/zip", json={"paths": []})
    assert res.status_code == 400


def test_zip_endpoint_builds_zip_with_requested_images(client):
    paths = ["AlbumA/1/pic1.jpg", "AlbumA/2/pic3.jpg"]
    res = client.post("/api/zip", json={"paths": paths})
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"


def test_zip_endpoint_reuses_cache_for_identical_request(client, zip_cache_dir):
    paths = ["AlbumA/1/pic1.jpg", "AlbumA/2/pic3.jpg"]
    first = client.post("/api/zip", json={"paths": paths})
    second = client.post("/api/zip", json={"paths": paths})
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.content == second.content
    zip_files = list(zip_cache_dir.glob("*.zip"))
    assert len(zip_files) == 1, f"expected exactly one cached zip, found {zip_files}"


def test_zip_endpoint_leaves_no_tmp_files_behind(client, zip_cache_dir):
    client.post("/api/zip", json={"paths": ["AlbumA/1/pic1.jpg"]})
    leftover_tmp = list(zip_cache_dir.glob("*.tmp"))
    assert leftover_tmp == []


def test_startup_cleans_up_stale_tmp_files(zip_cache_dir):
    from fastapi.testclient import TestClient
    from app.main import app

    zip_cache_dir.mkdir(parents=True, exist_ok=True)
    stray = zip_cache_dir / "abandoned.zip.tmp"
    stray.write_bytes(b"partial")
    with TestClient(app):
        pass
    assert not stray.exists()


def test_startup_and_shutdown_are_logged():
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app):
        pass
    rows = _db().execute(
        "SELECT event_type FROM events WHERE event_type IN ('server_started', 'server_stopping') ORDER BY id DESC LIMIT 2"
    ).fetchall()
    event_types = {r[0] for r in rows}
    assert "server_started" in event_types
    assert "server_stopping" in event_types


def test_event_logging(client):
    res = client.post("/api/event", json={"type": "test_event", "detail": "hello"})
    assert res.status_code == 200
    row = _db().execute(
        "SELECT event_type, detail FROM events WHERE event_type = 'test_event' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert row == ("test_event", "hello")


def test_voiceover_upload_list_and_detail(client):
    events = [
        {"t": 0.0, "path": "AlbumA/1/pic1.jpg", "x": 0.5, "y": 0.5},
        {"t": 2.0, "path": "AlbumA/2/pic3.jpg", "x": 0.2, "y": 0.8},
    ]
    import json as jsonlib

    res = client.post(
        "/api/voiceover",
        data={"events": jsonlib.dumps(events)},
        files={"audio": ("voiceover.webm", b"fake-audio-bytes", "audio/webm")},
    )
    assert res.status_code == 200

    listing = client.get("/api/voiceovers").json()
    assert len(listing) == 1
    assert listing[0]["image_count"] == 2

    detail = client.get(f"/api/voiceover/{listing[0]['id']}").json()
    assert detail["events"] == events

    audio_res = client.get(detail["audio_url"])
    assert audio_res.status_code == 200
    assert audio_res.content == b"fake-audio-bytes"


def test_voiceover_audio_rejects_path_traversal(client):
    res = client.get("/voiceover-audio/..%2F..%2Fetc%2Fpasswd")
    assert res.status_code in (400, 404)
