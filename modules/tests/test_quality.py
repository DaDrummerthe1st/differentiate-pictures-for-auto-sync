import numpy as np
from PIL import Image, ImageFilter

from modules.quality import check_blur, check_exposure, check_saturation, is_blurry


def _checkerboard(size: int = 64, square: int = 8) -> Image.Image:
    arr = np.zeros((size, size), dtype=np.uint8)
    for y in range(0, size, square):
        for x in range(0, size, square):
            if ((x // square) + (y // square)) % 2 == 0:
                arr[y : y + square, x : x + square] = 255
    return Image.fromarray(arr).convert("RGB")


def _solid(color: tuple[int, int, int]) -> Image.Image:
    return Image.new("RGB", (40, 30), color=color)


def test_check_blur_is_low_for_a_sharp_image(tmp_path):
    path = tmp_path / "sharp.png"
    _checkerboard().save(path)

    assert check_blur(str(path)) < 10.0


def test_check_blur_is_high_for_a_heavily_blurred_image(tmp_path):
    path = tmp_path / "blurred.png"
    _checkerboard().filter(ImageFilter.GaussianBlur(radius=6)).save(path)

    assert check_blur(str(path)) > 90.0


def test_check_blur_stays_within_0_to_100_bounds(tmp_path):
    path = tmp_path / "sharp.png"
    _checkerboard().save(path)

    assert 0.0 <= check_blur(str(path)) <= 100.0


def test_is_blurry_matches_the_50_percent_threshold(tmp_path):
    sharp_path = tmp_path / "sharp.png"
    blurred_path = tmp_path / "blurred.png"
    _checkerboard().save(sharp_path)
    _checkerboard().filter(ImageFilter.GaussianBlur(radius=6)).save(blurred_path)

    assert is_blurry(str(sharp_path)) is False
    assert is_blurry(str(blurred_path)) is True


def test_check_exposure_is_very_negative_for_a_black_image(tmp_path):
    path = tmp_path / "black.png"
    _solid((0, 0, 0)).save(path)

    assert check_exposure(str(path)) < -90.0


def test_check_exposure_is_very_positive_for_a_white_image(tmp_path):
    path = tmp_path / "white.png"
    _solid((255, 255, 255)).save(path)

    assert check_exposure(str(path)) > 90.0


def test_check_exposure_is_near_zero_for_a_balanced_gray_image(tmp_path):
    path = tmp_path / "gray.png"
    _solid((128, 128, 128)).save(path)

    assert abs(check_exposure(str(path))) < 5.0


def test_check_exposure_stays_within_bounds(tmp_path):
    path = tmp_path / "black.png"
    _solid((0, 0, 0)).save(path)

    assert -100.0 <= check_exposure(str(path)) <= 100.0


def test_check_saturation_is_low_for_a_grayscale_image(tmp_path):
    path = tmp_path / "gray.png"
    _solid((128, 128, 128)).save(path)

    assert check_saturation(str(path)) < 10.0


def test_check_saturation_is_high_for_a_vivid_color_image(tmp_path):
    path = tmp_path / "vivid.png"
    _solid((220, 20, 20)).save(path)

    assert check_saturation(str(path)) > 90.0


def test_check_saturation_stays_within_0_to_100_bounds(tmp_path):
    path = tmp_path / "vivid.png"
    _solid((220, 20, 20)).save(path)

    assert 0.0 <= check_saturation(str(path)) <= 100.0
