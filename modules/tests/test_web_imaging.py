import io
import tempfile

from PIL import Image

from modules.web.imaging import encode_jpeg, thumbnail


def test_thumbnail_scales_down_a_wide_image_to_fit_max_size():
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        Image.new("RGB", (2000, 1000), color=(0, 0, 0)).save(tmp.name)
        image = thumbnail(tmp.name, max_size=200)

    assert image.size == (200, 100)


def test_thumbnail_scales_down_a_tall_image_to_fit_max_size():
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        Image.new("RGB", (1000, 2000), color=(0, 0, 0)).save(tmp.name)
        image = thumbnail(tmp.name, max_size=200)

    assert image.size == (100, 200)


def test_thumbnail_leaves_a_small_image_unscaled():
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        Image.new("RGB", (50, 40), color=(0, 0, 0)).save(tmp.name)
        image = thumbnail(tmp.name, max_size=200)

    assert image.size == (50, 40)


def test_encode_jpeg_returns_bytes_decodable_as_the_same_size_image():
    image = Image.new("RGB", (30, 20), color=(200, 100, 50))

    encoded = encode_jpeg(image)

    assert isinstance(encoded, bytes)
    decoded = Image.open(io.BytesIO(encoded))
    assert decoded.size == (30, 20)
