import numpy as np
import pytest
from PIL import Image

from modules.objects import (
    COCO_CLASSES,
    Detection,
    DetectionResult,
    _decode_detections,
    _generate_center_priors,
    _letterbox,
    _nms,
)


def _solid_bgr(width: int, height: int, color: tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
    return np.full((height, width, 3), color, dtype=np.uint8)


def test_letterbox_pads_a_wider_than_tall_image_on_top_and_bottom():
    image = _solid_bgr(width=200, height=100)

    padded, scale, pad_x, pad_y = _letterbox(image, size=416)

    assert padded.shape == (416, 416, 3)
    assert scale == pytest.approx(416 / 200)
    assert pad_x == 0
    assert pad_y > 0


def test_letterbox_pads_a_taller_than_wide_image_on_left_and_right():
    image = _solid_bgr(width=100, height=200)

    padded, scale, pad_x, pad_y = _letterbox(image, size=416)

    assert padded.shape == (416, 416, 3)
    assert scale == pytest.approx(416 / 200)
    assert pad_x > 0
    assert pad_y == 0


def test_letterbox_leaves_a_square_image_unpadded():
    image = _solid_bgr(width=300, height=300)

    padded, scale, pad_x, pad_y = _letterbox(image, size=416)

    assert padded.shape == (416, 416, 3)
    assert scale == pytest.approx(416 / 300)
    assert pad_x == 0
    assert pad_y == 0


def test_generate_center_priors_covers_every_stride():
    strides = (8, 16, 32, 64)

    priors = _generate_center_priors(input_size=416, strides=strides)

    expected_points = sum((416 // s if 416 % s == 0 else 416 // s + 1) ** 2 for s in strides)
    assert priors.shape == (expected_points, 3)
    assert set(np.unique(priors[:, 2]).tolist()) == set(strides)


def test_nms_drops_the_lower_scoring_of_two_overlapping_boxes():
    boxes = np.array(
        [
            [10.0, 10.0, 50.0, 50.0],
            [12.0, 12.0, 52.0, 52.0],  # heavily overlaps the box above
            [200.0, 200.0, 240.0, 240.0],  # far away, should survive
        ]
    )
    scores = np.array([0.9, 0.8, 0.7])

    keep = _nms(boxes, scores, iou_threshold=0.5)

    assert sorted(keep) == [0, 2]


def test_nms_keeps_non_overlapping_boxes():
    boxes = np.array([[0.0, 0.0, 10.0, 10.0], [100.0, 100.0, 110.0, 110.0]])
    scores = np.array([0.6, 0.6])

    keep = _nms(boxes, scores, iou_threshold=0.5)

    assert sorted(keep) == [0, 1]


def _fabricated_model_output(class_index: int, class_score: float, reg_max: int = 7) -> np.ndarray:
    """Build a fake (1, N, 112) raw model output with exactly one confident
    detection at the first grid point, decoding to a small, fixed-size box."""
    strides = (8, 16, 32, 64)
    num_points = sum((416 // s if 416 % s == 0 else 416 // s + 1) ** 2 for s in strides)
    num_channels = 80 + (reg_max + 1) * 4
    output = np.zeros((1, num_points, num_channels), dtype=np.float32)
    output[0, 0, class_index] = class_score
    # For each of the 4 sides, put all softmax weight on bin index 2 so the
    # decoded distance for that side is exactly 2 * stride.
    for side in range(4):
        start = 80 + side * (reg_max + 1)
        output[0, 0, start + 2] = 10.0  # softmax(10, 0, 0, ...) ~= 1.0 on bin 2
    return output


def test_decode_detections_finds_the_single_fabricated_detection():
    raw_output = _fabricated_model_output(class_index=16, class_score=0.9)  # 16 = "dog"

    detections = _decode_detections(
        raw_output,
        input_size=416,
        strides=(8, 16, 32, 64),
        reg_max=7,
        score_threshold=0.4,
        nms_threshold=0.5,
    )

    assert len(detections) == 1
    det = detections[0]
    assert det.class_name == "dog"
    assert det.confidence == pytest.approx(0.9)
    # First grid point of the first (smallest) stride is at (0, 0), stride 8,
    # so distance 2*8=16 on every side: box = (0-16, 0-16, 0+16, 0+16), clipped to >= 0.
    assert det.bbox == (0, 0, 16, 16)


def test_decode_detections_returns_nothing_below_score_threshold():
    raw_output = _fabricated_model_output(class_index=16, class_score=0.1)

    detections = _decode_detections(
        raw_output,
        input_size=416,
        strides=(8, 16, 32, 64),
        reg_max=7,
        score_threshold=0.4,
        nms_threshold=0.5,
    )

    assert detections == []


def test_coco_classes_has_80_unique_names():
    assert len(COCO_CLASSES) == 80
    assert len(set(COCO_CLASSES)) == 80
    assert "dog" in COCO_CLASSES
    assert "person" in COCO_CLASSES


def test_detect_objects_scales_boxes_back_to_original_image_size(tmp_path, monkeypatch):
    from modules import objects

    path = tmp_path / "wide.png"
    Image.fromarray(np.zeros((100, 200, 3), dtype=np.uint8)).save(path)

    fake_detection = Detection(class_name="dog", confidence=0.9, bbox=(0, 0, 16, 16))

    def fake_decode(*args, **kwargs):
        return [fake_detection]

    class FakeSession:
        def get_inputs(self):
            class _In:
                name = "data"

            return [_In()]

        def run(self, output_names, feeds):
            return [np.zeros((1, 1, 112), dtype=np.float32)]

    monkeypatch.setattr(objects, "_decode_detections", fake_decode)
    monkeypatch.setattr(objects, "_load_session", lambda: FakeSession())

    result = objects.detect_objects(str(path))

    assert isinstance(result, DetectionResult)
    assert result.image_width == 200
    assert result.image_height == 100
    assert len(result.detections) == 1
    # 200x100 original was letterboxed into 416x416 at scale 416/200, padded
    # on top/bottom -- the fabricated (0,0,16,16) box in padded-image space
    # must be un-padded and un-scaled back to original pixel coordinates.
    got = result.detections[0]
    assert got.class_name == "dog"
    assert 0 <= got.bbox[0] <= got.bbox[2] <= 200
    assert 0 <= got.bbox[1] <= got.bbox[3] <= 100


def test_has_object_is_true_when_the_class_is_present(tmp_path, monkeypatch):
    from modules import objects

    path = tmp_path / "img.png"
    Image.fromarray(np.zeros((50, 50, 3), dtype=np.uint8)).save(path)

    fake_result = DetectionResult(
        detections=[Detection(class_name="dog", confidence=0.9, bbox=(1, 1, 2, 2))],
        image_width=50,
        image_height=50,
    )
    monkeypatch.setattr(objects, "detect_objects", lambda *a, **k: fake_result)

    assert objects.has_object(str(path), "dog") is True
    assert objects.has_object(str(path), "cat") is False


def test_has_object_rejects_an_unknown_class_name(tmp_path):
    from modules import objects

    path = tmp_path / "img.png"
    Image.fromarray(np.zeros((50, 50, 3), dtype=np.uint8)).save(path)

    with pytest.raises(ValueError):
        objects.has_object(str(path), "not-a-real-coco-class")
