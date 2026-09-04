import os

import cv2
import numpy as np
from PIL import Image

# Overridable via env, never hardcoded past this point - see
# documentation/curation/TODO.md's build plan, Phase 3.
FACE_SCORE_THRESHOLD = float(os.environ.get("FACE_SCORE_THRESHOLD", "0.6"))

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "face_detection_yunet_2023mar.onnx")

_detector: cv2.FaceDetectorYN | None = None


def _get_detector(input_size: tuple[int, int]) -> cv2.FaceDetectorYN:
    global _detector
    if _detector is None:
        _detector = cv2.FaceDetectorYN_create(
            _MODEL_PATH, "", input_size, score_threshold=FACE_SCORE_THRESHOLD
        )
    else:
        _detector.setInputSize(input_size)
    return _detector


def detect_faces(image: Image.Image) -> list[dict]:
    bgr = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    height, width = bgr.shape[:2]
    detector = _get_detector((width, height))
    _, faces = detector.detect(bgr)
    if faces is None:
        return []

    # Normalized 0..1 fractions of width/height, not pixel coordinates -
    # matches app/main.py's TagCreate/_validate_tag_fields storage format
    # (0 <= bbox_x <= 1, bbox_x + bbox_w <= 1), confirmed by reading that
    # validation rather than assumed. Also clamps YuNet's raw box to the
    # image bounds first, since a detection near an edge can extend
    # slightly past it, which that same validation rejects outright.
    results = []
    for face in faces:
        x, y, w, h = (float(v) for v in face[:4])
        x0 = max(0.0, x)
        y0 = max(0.0, y)
        x1 = min(float(width), x + w)
        y1 = min(float(height), y + h)
        box_w = x1 - x0
        box_h = y1 - y0
        if box_w <= 0 or box_h <= 0:
            continue
        results.append(
            {
                "bbox_x": x0 / width,
                "bbox_y": y0 / height,
                "bbox_w": box_w / width,
                "bbox_h": box_h / height,
            }
        )
    return results
