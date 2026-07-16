import sqlite3

from app.main import DB_PATH


def _db():
    return sqlite3.connect(DB_PATH)


def test_file_summary_totals_all_files_regardless_of_extension(client):
    res = client.get("/api/file-summary")
    assert res.status_code == 200
    data = res.json()
    # AlbumA/1: pic1.jpg, pic2.jpg, clip.avi, doc.pdf, other_report.pdf
    # AlbumA/2: pic3.jpg
    # AlbumA: junk.exe, junk.dll, notes.txt, fake_photo.jpg
    assert data["total_files"] == 10


def test_file_summary_detects_real_type_from_content_not_extension(client):
    res = client.get("/api/file-summary")
    categories = {c["label"]: c["count"] for c in res.json()["categories"]}
    assert categories.get("JPEG-bild", 0) == 3  # pic1.jpg, pic2.jpg, pic3.jpg
    assert categories.get("Windows-program/DLL (MZ)", 0) == 2  # junk.exe, junk.dll
    assert categories.get("PDF-dokument", 0) == 2
    assert categories.get("AVI-video", 0) == 1
    assert categories.get("Textfil", 0) == 2  # notes.txt, and fake_photo.jpg (really text)


def test_file_summary_flags_extension_content_mismatch(client):
    res = client.get("/api/file-summary")
    mismatches = res.json()["extension_mismatches"]
    paths = [m["path"] for m in mismatches]
    assert "AlbumA/fake_photo.jpg" in paths
    mismatch = next(m for m in mismatches if m["path"] == "AlbumA/fake_photo.jpg")
    assert mismatch["extension"] == ".jpg"
    assert mismatch["detected"] != "JPEG-bild"


def test_file_summary_does_not_flag_correctly_typed_media(client):
    res = client.get("/api/file-summary")
    mismatches = res.json()["extension_mismatches"]
    paths = [m["path"] for m in mismatches]
    assert "AlbumA/1/pic1.jpg" not in paths
    assert "AlbumA/1/doc.pdf" not in paths


def test_tree_groups_by_headline_and_immediate_parent_chunk(client):
    res = client.get("/api/tree")
    assert res.status_code == 200
    sections = res.json()
    assert len(sections) == 1
    section = sections[0]
    assert section["headline"] == "AlbumA"
    chunks = {c["path"]: c["images"] for c in section["chunks"]}
    assert chunks["AlbumA/1"] == [
        "AlbumA/1/clip.avi",
        "AlbumA/1/doc.pdf",
        "AlbumA/1/other_report.pdf",
        "AlbumA/1/pic1.jpg",
        "AlbumA/1/pic2.jpg",
    ]
    assert chunks["AlbumA/2"] == ["AlbumA/2/pic3.jpg"]


def test_tree_excludes_non_image_files(client):
    res = client.get("/api/tree")
    all_images = [img for h in res.json() for c in h["chunks"] for img in c["images"]]
    assert not any(img.endswith(".exe") for img in all_images)


def test_tree_includes_video_and_pdf_media(client):
    res = client.get("/api/tree")
    all_images = [img for h in res.json() for c in h["chunks"] for img in c["images"]]
    assert "AlbumA/1/clip.avi" in all_images
    assert "AlbumA/1/doc.pdf" in all_images


def test_tree_excludes_binaries(client):
    res = client.get("/api/tree")
    all_images = [img for h in res.json() for c in h["chunks"] for img in c["images"]]
    assert not any(img.endswith(".dll") for img in all_images)


def test_tree_excludes_extension_content_mismatches(client):
    # fake_photo.jpg has a .jpg extension but isn't really a JPEG - it
    # must not be browsable/thumbnailable as if it were a real photo.
    res = client.get("/api/tree")
    all_images = [img for h in res.json() for c in h["chunks"] for img in c["images"]]
    assert "AlbumA/fake_photo.jpg" not in all_images


def test_file_summary_still_reports_mismatches_excluded_from_tree(client):
    # Even though it's hidden from browsing, it must still be visible
    # in the file-type summary so a user can go check it.
    res = client.get("/api/file-summary")
    paths = [m["path"] for m in res.json()["extension_mismatches"]]
    assert "AlbumA/fake_photo.jpg" in paths


def test_thumb_for_corrupt_picture_returns_placeholder_not_500(client):
    # fake_photo.jpg has a .jpg extension but its real content isn't a
    # valid JPEG (see conftest) - the thumbnailer must not crash on it.
    res = client.get("/thumb", params={"p": "AlbumA/fake_photo.jpg"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/jpeg"


def test_thumb_for_video_returns_placeholder_not_crash(client):
    res = client.get("/thumb", params={"p": "AlbumA/1/clip.avi"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/jpeg"
    assert len(res.content) > 0


def test_thumb_for_pdf_returns_placeholder_not_crash(client):
    res = client.get("/thumb", params={"p": "AlbumA/1/doc.pdf"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/jpeg"
    assert len(res.content) > 0


def test_original_serves_video_with_video_mime(client):
    res = client.get("/original", params={"p": "AlbumA/1/clip.avi"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "video/x-msvideo"


def test_original_serves_pdf_with_pdf_mime(client):
    res = client.get("/original", params={"p": "AlbumA/1/doc.pdf"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"


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
