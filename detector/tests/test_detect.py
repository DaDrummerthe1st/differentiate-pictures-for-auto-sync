import io

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from detector.main import app

client = TestClient(app)


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
