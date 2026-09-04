import os

import pytest
from PIL import Image

from detector.faces import detect_faces

# Real, disposable photos (resources/test_pictures/, gitignored) - not
# synthetic fixtures, since YuNet is trained on real faces and a synthetic
# checkerboard proves nothing about it. Skips (not fails) when the fixture
# tree isn't present on the machine running the tests, same reasoning as
# any other locally-fetched, gitignored test asset.
_FIXTURE_ROOT = "resources/test_pictures/Florida1/Florida/1"
_FACE_PHOTO = os.path.join(_FIXTURE_ROOT, "IMGP0128.JPG")
_NO_FACE_PHOTOS = [
    os.path.join(_FIXTURE_ROOT, "IMGP0150.JPG"),
    os.path.join(_FIXTURE_ROOT, "IMGP0135.JPG"),
]

_fixtures_present = os.path.exists(_FACE_PHOTO) and all(os.path.exists(p) for p in _NO_FACE_PHOTOS)

pytestmark = pytest.mark.skipif(
    not _fixtures_present,
    reason="resources/test_pictures/Florida1 fixture tree not present on this machine",
)


def test_detect_faces_finds_the_one_clear_face():
    image = Image.open(_FACE_PHOTO)

    faces = detect_faces(image)

    assert len(faces) == 1
    face = faces[0]
    for key in ("bbox_x", "bbox_y", "bbox_w", "bbox_h"):
        assert isinstance(face[key], float)
        assert 0 <= face[key] <= 1
    assert face["bbox_w"] > 0
    assert face["bbox_h"] > 0
    assert face["bbox_x"] + face["bbox_w"] <= 1
    assert face["bbox_y"] + face["bbox_h"] <= 1


@pytest.mark.parametrize("path", _NO_FACE_PHOTOS)
def test_detect_faces_finds_nothing_in_a_people_free_photo(path):
    image = Image.open(path)

    assert detect_faces(image) == []
