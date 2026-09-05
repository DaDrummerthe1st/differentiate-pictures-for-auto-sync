import pytest
from PIL import Image

from modules.web.server import handle_detail, handle_image, handle_scan, handle_scan_page, handle_grid


def _save_photo(path, width=64, height=48, color=(10, 20, 30)):
    Image.new("RGB", (width, height), color=color).save(path)


def test_handle_scan_registers_the_folder_and_returns_a_redirect_url(tmp_path):
    folder = tmp_path / "photos"
    folder.mkdir()
    _save_photo(folder / "a.jpg")
    db_path = tmp_path / "app.db"

    redirect_url = handle_scan(str(folder), "", db_path=str(db_path))

    assert redirect_url == f"/pictures?folder={str(folder).replace('/', '%2F')}&page=0"


def test_handle_scan_rejects_a_nonexistent_folder(tmp_path):
    with pytest.raises(ValueError):
        handle_scan(str(tmp_path / "nope"), "", db_path=str(tmp_path / "app.db"))


def test_handle_scan_page_renders_the_folder_form():
    html = handle_scan_page()

    assert "<form" in html


def test_handle_grid_shows_registered_pictures_for_that_folder(tmp_path):
    folder = tmp_path / "photos"
    folder.mkdir()
    _save_photo(folder / "a.jpg")
    db_path = tmp_path / "app.db"
    handle_scan(str(folder), "", db_path=str(db_path))

    html = handle_grid(f"folder={str(folder)}&page=0", db_path=str(db_path))

    assert "a.jpg" in html


def test_handle_grid_reports_when_nothing_is_registered_under_that_folder(tmp_path):
    db_path = tmp_path / "app.db"
    html = handle_grid(f"folder={tmp_path}&page=0", db_path=str(db_path))

    assert "no pictures" in html.lower()


def test_handle_detail_shows_findings_for_the_given_location(tmp_path, monkeypatch):
    folder = tmp_path / "photos"
    folder.mkdir()
    _save_photo(folder / "a.jpg")
    db_path = tmp_path / "app.db"
    from modules.pictures import GetListOfValidPictureFiles

    registered = GetListOfValidPictureFiles(str(folder), db_path=str(db_path))[0]

    html = handle_detail(registered.location_id, db_path=str(db_path), folder=str(folder), page="0")

    assert "a.jpg" in html
    assert "Quality" in html


def test_handle_detail_rejects_an_unknown_location_id(tmp_path):
    with pytest.raises(ValueError):
        handle_detail("no-such-id", db_path=str(tmp_path / "app.db"), folder="/x", page="0")


def test_handle_image_thumb_variant_returns_jpeg_bytes(tmp_path):
    folder = tmp_path / "photos"
    folder.mkdir()
    _save_photo(folder / "a.jpg")
    db_path = tmp_path / "app.db"
    from modules.pictures import GetListOfValidPictureFiles

    registered = GetListOfValidPictureFiles(str(folder), db_path=str(db_path))[0]

    image_bytes = handle_image(registered.location_id, "thumb", db_path=str(db_path))

    assert image_bytes[:2] == b"\xff\xd8"  # JPEG magic bytes


def test_handle_image_full_variant_returns_jpeg_bytes(tmp_path):
    folder = tmp_path / "photos"
    folder.mkdir()
    _save_photo(folder / "a.jpg")
    db_path = tmp_path / "app.db"
    from modules.pictures import GetListOfValidPictureFiles

    registered = GetListOfValidPictureFiles(str(folder), db_path=str(db_path))[0]

    image_bytes = handle_image(registered.location_id, "full", db_path=str(db_path))

    assert image_bytes[:2] == b"\xff\xd8"


def test_handle_image_rejects_an_unknown_location_id(tmp_path):
    with pytest.raises(ValueError):
        handle_image("no-such-id", "thumb", db_path=str(tmp_path / "app.db"))
