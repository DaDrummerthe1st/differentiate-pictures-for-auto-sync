import numpy as np
from PIL import Image, ImageFilter

from detector.quality import detect_blur, detect_exposure, detect_monochrome


def _checkerboard(size: int = 64, square: int = 8) -> Image.Image:
    arr = np.zeros((size, size), dtype=np.uint8)
    for y in range(0, size, square):
        for x in range(0, size, square):
            if ((x // square) + (y // square)) % 2 == 0:
                arr[y : y + square, x : x + square] = 255
    return Image.fromarray(arr).convert("RGB")


def _solid(color: tuple[int, int, int]) -> Image.Image:
    return Image.new("RGB", (40, 30), color=color)


def test_detect_blur_flags_a_heavily_blurred_image():
    sharp = _checkerboard()
    blurred = sharp.filter(ImageFilter.GaussianBlur(radius=6))

    assert detect_blur(sharp) is False
    assert detect_blur(blurred) is True


def test_detect_exposure_flags_overexposed_and_underexposed():
    assert detect_exposure(_solid((255, 255, 255))) == "overexposed"
    assert detect_exposure(_solid((0, 0, 0))) == "underexposed"
    assert detect_exposure(_solid((128, 128, 128))) is None


def test_detect_monochrome_flags_grayscale_not_saturated_color():
    assert detect_monochrome(_solid((128, 128, 128))) is True
    assert detect_monochrome(_solid((220, 20, 20))) is False
