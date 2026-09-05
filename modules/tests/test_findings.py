import numpy as np
from PIL import Image

from modules.findings import annotate, exif_lines, format_exposure_time, gps_to_decimal
from modules.objects import Detection, DetectionResult


def _save_photo(path, width=100, height=60, color=(10, 20, 30)):
    Image.new("RGB", (width, height), color=color).save(path)


def test_format_exposure_time_for_a_second_or_longer():
    assert format_exposure_time(2.0) == "2.0s"


def test_format_exposure_time_for_a_fraction_of_a_second():
    assert format_exposure_time(1 / 250) == "1/250s"


def test_gps_to_decimal_returns_none_without_dms_or_ref():
    assert gps_to_decimal(None, "N") is None
    assert gps_to_decimal((59, 20, 0), None) is None


def test_gps_to_decimal_is_positive_for_north_and_east():
    assert gps_to_decimal((59, 30, 0), "N") == 59.5


def test_gps_to_decimal_is_negative_for_south_and_west():
    assert gps_to_decimal((59, 30, 0), "S") == -59.5


def test_exif_lines_reports_none_when_the_image_has_no_exif(tmp_path):
    path = tmp_path / "plain.png"
    _save_photo(path)

    assert exif_lines(str(path)) == ["(none)"]


def test_exif_lines_reports_camera_make_and_model(tmp_path):
    path = tmp_path / "with_exif.jpg"
    image = Image.new("RGB", (100, 60), color=(10, 20, 30))
    exif = image.getexif()
    exif[271] = "Acme"  # Make
    exif[272] = "Camera 3000"  # Model
    image.save(path, exif=exif.tobytes())

    lines = exif_lines(str(path))

    assert any("Acme" in line and "Camera 3000" in line for line in lines)


def test_annotate_scales_down_an_image_wider_than_max_display_width():
    path_width, path_height = 1800, 900
    result = DetectionResult(detections=[], image_width=path_width, image_height=path_height)

    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        Image.new("RGB", (path_width, path_height), color=(0, 0, 0)).save(tmp.name)
        annotated = annotate(tmp.name, result, max_display_width=900)

    assert annotated.size == (900, 450)


def test_annotate_draws_a_box_for_each_detection():
    width, height = 200, 100
    detection = Detection(class_name="dog", confidence=0.9, bbox=(10, 10, 50, 50))
    result = DetectionResult(detections=[detection], image_width=width, image_height=height)

    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        Image.new("RGB", (width, height), color=(255, 255, 255)).save(tmp.name)
        annotated = annotate(tmp.name, result, max_display_width=900)

    # Box drawn in red somewhere on the (unscaled, since 200 < 900) image.
    assert annotated.size == (width, height)
    pixels = np.array(annotated).reshape(-1, 3)
    assert any((pixels == (255, 0, 0)).all(axis=1))


def test_annotate_raises_when_detection_size_does_not_match_the_actual_image():
    result = DetectionResult(detections=[], image_width=999, image_height=999)

    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        Image.new("RGB", (10, 10), color=(0, 0, 0)).save(tmp.name)
        try:
            annotate(tmp.name, result)
            assert False, "expected an AssertionError"
        except AssertionError:
            pass
