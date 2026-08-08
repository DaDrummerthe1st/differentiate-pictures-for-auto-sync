import io
import os

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from detector.main import MAX_UPLOAD_BYTES, app

client = TestClient(app)

# Real, disposable fixture (resources/test_pictures/, gitignored) - same
# fixture used in test_faces.py's unit tests for detect_faces itself.
_FACE_PHOTO = "resources/test_pictures/Florida1/Florida/1/IMGP0128.JPG"


def _checkerboard(color_a: tuple, color_b: tuple, size: int = 64, square: int = 8) -> Image.Image:
    # Solid-color fixtures are degenerate for detect_blur (zero-variance,
    # always "blurry") - every fixture here keeps some edge content so
    # each test isolates the one signal it's asserting on, confirmed
    # against real detect_blur/detect_exposure/detect_monochrome output
    # rather than assumed.
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    for y in range(0, size, square):
        for x in range(0, size, square):
            color = color_a if ((x // square) + (y // square)) % 2 == 0 else color_b
            arr[y : y + square, x : x + square] = color
    return Image.fromarray(arr)


def _upload(image: Image.Image):
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    buf.seek(0)
    return client.post("/detect", files={"file": ("test.jpg", buf, "image/jpeg")})


def test_detect_returns_no_quality_tags_for_a_normal_photo():
    image = _checkerboard((220, 20, 20), (20, 20, 220))

    res = _upload(image)

    assert res.status_code == 200
    assert res.json() == {"tags": []}


def test_detect_flags_overexposed():
    image = _checkerboard((255, 255, 255), (216, 216, 216))

    res = _upload(image)

    assert res.status_code == 200
    tags = res.json()["tags"]
    values = {tag["value"] for tag in tags}
    assert "overexposed" in values
    assert "blurry" not in values
    for tag in tags:
        assert tag["category"] == "generic"
        assert tag["bbox_x"] is None
        assert tag["bbox_y"] is None
        assert tag["bbox_w"] is None
        assert tag["bbox_h"] is None


def test_detect_flags_underexposed():
    image = _checkerboard((0, 0, 0), (39, 39, 39))

    res = _upload(image)

    values = {tag["value"] for tag in res.json()["tags"]}
    assert "underexposed" in values
    assert "blurry" not in values


def test_detect_flags_monochrome_only_for_a_grayscale_photo():
    image = _checkerboard((0, 0, 0), (255, 255, 255))

    res = _upload(image)

    assert res.status_code == 200
    assert res.json() == {
        "tags": [
            {
                "category": "generic",
                "value": "black_and_white",
                "bbox_x": None,
                "bbox_y": None,
                "bbox_w": None,
                "bbox_h": None,
            }
        ]
    }


def test_detect_flags_blur_for_a_flat_untextured_photo():
    image = Image.new("RGB", (40, 30), color=(128, 128, 128))

    res = _upload(image)

    values = {tag["value"] for tag in res.json()["tags"]}
    assert values == {"blurry", "black_and_white"}


def test_detect_rejects_a_non_image_upload():
    buf = io.BytesIO(b"this is not an image")

    res = client.post("/detect", files={"file": ("notes.txt", buf, "text/plain")})

    assert res.status_code == 400


@pytest.mark.skipif(
    not os.path.exists(_FACE_PHOTO),
    reason="resources/test_pictures/Florida1 fixture tree not present on this machine",
)
def test_detect_flags_a_face_with_a_bbox():
    with open(_FACE_PHOTO, "rb") as f:
        res = client.post("/detect", files={"file": ("face.jpg", f, "image/jpeg")})

    assert res.status_code == 200
    people_tags = [tag for tag in res.json()["tags"] if tag["category"] == "people"]
    assert len(people_tags) == 1
    tag = people_tags[0]
    assert tag["value"] == "Person"
    assert tag["bbox_w"] > 0
    assert tag["bbox_h"] > 0


def test_detect_include_timing_reports_per_detector_cpu_time():
    image = _checkerboard((220, 20, 20), (20, 20, 220))
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    buf.seek(0)

    res = client.post(
        "/detect", params={"include_timing": "true"}, files={"file": ("test.jpg", buf, "image/jpeg")}
    )

    assert res.status_code == 200
    data = res.json()
    assert "timings" in data
    cpu_time_ms = data["timings"]["cpu_time_ms"]
    assert set(cpu_time_ms) == {"blur", "exposure", "monochrome", "face"}
    for value in cpu_time_ms.values():
        assert value >= 0
    assert data["timings"]["peak_rss_kb"] > 0


def test_detect_omits_timings_by_default():
    image = _checkerboard((220, 20, 20), (20, 20, 220))

    res = _upload(image)

    assert "timings" not in res.json()


def test_detect_rejects_an_oversized_upload():
    # Resource-exhaustion guard, THREATS.md #16 - checked in chunks, before
    # a full PIL decode is ever attempted, not just an after-the-fact size
    # check once the whole body is already buffered.
    buf = io.BytesIO(b"x" * (MAX_UPLOAD_BYTES + 1))

    res = client.post("/detect", files={"file": ("huge.jpg", buf, "image/jpeg")})

    assert res.status_code == 413
