import os
import sqlite3

from PIL import Image

from modules.pictures import (
    GetListOfValidPictureFiles,
    _file_metadata,
    _is_valid_picture_file,
    _md5,
    _statx_birth_time,
)


def _save_photo(path, color=(10, 20, 30)):
    Image.new("RGB", (16, 16), color=color).save(path)


def test_is_valid_picture_file_true_for_a_real_photo(tmp_path):
    path = tmp_path / "photo.jpg"
    _save_photo(path)

    assert _is_valid_picture_file(str(path)) is True


def test_is_valid_picture_file_false_for_a_non_picture_extension(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("not a picture")

    assert _is_valid_picture_file(str(path)) is False


def test_is_valid_picture_file_false_for_garbage_bytes_with_a_picture_extension(tmp_path):
    path = tmp_path / "fake.jpg"
    path.write_bytes(b"this is not really a jpeg")

    assert _is_valid_picture_file(str(path)) is False


def test_md5_matches_for_identical_content_at_different_paths(tmp_path):
    path_a = tmp_path / "a.jpg"
    path_b = tmp_path / "b.jpg"
    _save_photo(path_a, color=(1, 2, 3))
    _save_photo(path_b, color=(1, 2, 3))

    assert _md5(str(path_a)) == _md5(str(path_b))


def test_md5_differs_for_different_content(tmp_path):
    path_a = tmp_path / "a.jpg"
    path_b = tmp_path / "b.jpg"
    _save_photo(path_a, color=(1, 2, 3))
    _save_photo(path_b, color=(4, 5, 6))

    assert _md5(str(path_a)) != _md5(str(path_b))


def test_statx_birth_time_returns_a_real_value_when_available(tmp_path):
    path = tmp_path / "photo.jpg"
    _save_photo(path)

    birth_time, available = _statx_birth_time(str(path))

    assert available is True
    assert birth_time > 0


def test_statx_birth_time_reports_unavailable_rather_than_raising_for_a_missing_file():
    birth_time, available = _statx_birth_time("/no/such/path/at/all.jpg")

    assert available is False
    assert birth_time is None


def test_file_metadata_has_expected_keys(tmp_path):
    path = tmp_path / "photo.jpg"
    _save_photo(path)

    metadata = _file_metadata(str(path))

    assert metadata["filename"] == "photo.jpg"
    assert metadata["size"] > 0
    assert "mtime" in metadata
    assert "ctime" in metadata
    assert "mode" in metadata
    assert "birth_time" in metadata
    assert "birth_time_available" in metadata


def test_registers_valid_pictures_and_skips_non_pictures(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    _save_photo(folder / "keep.jpg")
    (folder / "skip.txt").write_text("not a picture")
    db_path = tmp_path / "pictures.db"

    results = GetListOfValidPictureFiles(str(folder), db_path=str(db_path))

    assert len(results) == 1
    assert results[0].path.endswith("keep.jpg")


def test_walks_nested_subfolders(tmp_path):
    folder = tmp_path / "folder"
    (folder / "nested").mkdir(parents=True)
    _save_photo(folder / "top.jpg")
    _save_photo(folder / "nested" / "deep.jpg")
    db_path = tmp_path / "pictures.db"

    results = GetListOfValidPictureFiles(str(folder), db_path=str(db_path))

    assert {os.path.basename(r.path) for r in results} == {"top.jpg", "deep.jpg"}


def test_same_content_at_two_paths_is_one_picture_with_two_locations(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    _save_photo(folder / "original.jpg", color=(9, 8, 7))
    _save_photo(folder / "copy.jpg", color=(9, 8, 7))
    db_path = tmp_path / "pictures.db"

    results = GetListOfValidPictureFiles(str(folder), db_path=str(db_path))

    assert len(results) == 2
    picture_ids = {r.picture_id for r in results}
    assert len(picture_ids) == 1
    md5s = {r.md5 for r in results}
    assert len(md5s) == 1


def test_rescanning_unchanged_folder_does_not_duplicate_locations(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    _save_photo(folder / "photo.jpg")
    db_path = tmp_path / "pictures.db"

    GetListOfValidPictureFiles(str(folder), db_path=str(db_path))
    second_results = GetListOfValidPictureFiles(str(folder), db_path=str(db_path))

    conn = sqlite3.connect(str(db_path))
    location_count = conn.execute("SELECT COUNT(*) FROM locations").fetchone()[0]
    conn.close()

    assert len(second_results) == 1
    assert location_count == 1


def test_rescanning_unchanged_file_does_not_rehash_it(tmp_path, monkeypatch):
    folder = tmp_path / "folder"
    folder.mkdir()
    _save_photo(folder / "photo.jpg")
    db_path = tmp_path / "pictures.db"

    GetListOfValidPictureFiles(str(folder), db_path=str(db_path))

    calls = []
    import modules.pictures as pictures_module

    original_md5 = pictures_module._md5

    def _counting_md5(path):
        calls.append(path)
        return original_md5(path)

    monkeypatch.setattr(pictures_module, "_md5", _counting_md5)

    GetListOfValidPictureFiles(str(folder), db_path=str(db_path))

    assert calls == []


def test_source_label_is_stored_per_location(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    _save_photo(folder / "photo.jpg")
    db_path = tmp_path / "pictures.db"

    results = GetListOfValidPictureFiles(str(folder), source="nas_pechakucha", db_path=str(db_path))

    assert results[0].source == "nas_pechakucha"


def test_same_path_rehashed_when_content_changes(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    path = folder / "photo.jpg"
    _save_photo(path, color=(1, 1, 1))
    db_path = tmp_path / "pictures.db"

    first = GetListOfValidPictureFiles(str(folder), db_path=str(db_path))

    _save_photo(path, color=(2, 2, 2))
    second = GetListOfValidPictureFiles(str(folder), db_path=str(db_path))

    conn = sqlite3.connect(str(db_path))
    location_count = conn.execute("SELECT COUNT(*) FROM locations").fetchone()[0]
    picture_count = conn.execute("SELECT COUNT(*) FROM pictures").fetchone()[0]
    conn.close()

    assert first[0].md5 != second[0].md5
    assert location_count == 1
    assert picture_count == 2
