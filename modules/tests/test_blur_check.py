import numpy as np
from PIL import Image, ImageFilter

from modules.blur_check import blur_percent, is_blurry


def _checkerboard(size: int = 64, square: int = 8) -> Image.Image:
    arr = np.zeros((size, size), dtype=np.uint8)
    for y in range(0, size, square):
        for x in range(0, size, square):
            if ((x // square) + (y // square)) % 2 == 0:
                arr[y : y + square, x : x + square] = 255
    return Image.fromarray(arr).convert("RGB")


def test_blur_percent_is_low_for_a_sharp_image(tmp_path):
    path = tmp_path / "sharp.png"
    _checkerboard().save(path)

    assert blur_percent(str(path)) < 10.0


def test_blur_percent_is_high_for_a_heavily_blurred_image(tmp_path):
    path = tmp_path / "blurred.png"
    _checkerboard().filter(ImageFilter.GaussianBlur(radius=6)).save(path)

    assert blur_percent(str(path)) > 90.0


def test_blur_percent_stays_within_0_to_100_bounds(tmp_path):
    path = tmp_path / "sharp.png"
    _checkerboard().save(path)

    assert 0.0 <= blur_percent(str(path)) <= 100.0


def test_is_blurry_matches_the_50_percent_threshold(tmp_path):
    sharp_path = tmp_path / "sharp.png"
    blurred_path = tmp_path / "blurred.png"
    _checkerboard().save(sharp_path)
    _checkerboard().filter(ImageFilter.GaussianBlur(radius=6)).save(blurred_path)

    assert is_blurry(str(sharp_path)) is False
    assert is_blurry(str(blurred_path)) is True
