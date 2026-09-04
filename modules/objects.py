"""Standalone object detector: NanoDet-Plus (Apache-2.0), COCO's 80 classes.
Self-contained - no dependency on detector/ or any other existing code in
this repo, same pattern as modules/quality.py.

Usage: python3 -m modules.objects <path-to-image>
"""
import os
import sys
from dataclasses import dataclass

import cv2
import numpy as np
import onnxruntime as ort

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "nanodet-plus-m_416.onnx")
INPUT_SIZE = 416
STRIDES = (8, 16, 32, 64)
REG_MAX = 7

# BGR-order mean/std this model was trained with (config/nanodet-plus-m_416.yml
# in the upstream repo) - not baked into the plain ONNX export, so applied here.
NORMALIZE_MEAN = np.array([103.53, 116.28, 123.675], dtype=np.float32)
NORMALIZE_STD = np.array([57.375, 57.12, 58.395], dtype=np.float32)

# NanoDet-Plus's own defaults (demo_openvino/main.cpp), not re-derived here.
SCORE_THRESHOLD = float(os.environ.get("OBJECTS_SCORE_THRESHOLD", "0.4"))
NMS_THRESHOLD = float(os.environ.get("OBJECTS_NMS_THRESHOLD", "0.5"))

COCO_CLASSES = (
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog",
    "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
    "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
    "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle",
    "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich",
    "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote",
    "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book",
    "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush",
)


@dataclass(frozen=True)
class Detection:
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]  # x1, y1, x2, y2 in pixel coordinates


@dataclass(frozen=True)
class DetectionResult:
    detections: list[Detection]
    image_width: int
    image_height: int


def _letterbox(image_bgr: np.ndarray, size: int) -> tuple[np.ndarray, float, int, int]:
    """Resize preserving aspect ratio to fit within size x size, centered on
    a black size x size canvas. Returns (padded_image, scale, pad_x, pad_y)."""
    height, width = image_bgr.shape[:2]
    scale = min(size / width, size / height)
    new_width, new_height = int(round(width * scale)), int(round(height * scale))
    resized = cv2.resize(image_bgr, (new_width, new_height))

    padded = np.zeros((size, size, 3), dtype=np.uint8)
    pad_x = (size - new_width) // 2
    pad_y = (size - new_height) // 2
    padded[pad_y : pad_y + new_height, pad_x : pad_x + new_width] = resized
    return padded, scale, pad_x, pad_y


def _generate_center_priors(input_size: int, strides: tuple[int, ...]) -> np.ndarray:
    """Grid points (x, y, stride) for every feature-map cell across all strides."""
    priors = []
    for stride in strides:
        feat_size = -(-input_size // stride)  # ceil division
        xs, ys = np.meshgrid(np.arange(feat_size), np.arange(feat_size))
        stride_col = np.full(xs.size, stride)
        priors.append(np.stack([xs.ravel(), ys.ravel(), stride_col], axis=1))
    return np.concatenate(priors, axis=0)


def _softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    shifted = x - np.max(x, axis=axis, keepdims=True)
    exp = np.exp(shifted)
    return exp / np.sum(exp, axis=axis, keepdims=True)


def _nms(boxes: np.ndarray, scores: np.ndarray, iou_threshold: float) -> list[int]:
    """Greedy NMS, same algorithm as NanoDet's own reference implementation."""
    order = scores.argsort()[::-1]
    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(int(i))
        rest = order[1:]

        xx1 = np.maximum(x1[i], x1[rest])
        yy1 = np.maximum(y1[i], y1[rest])
        xx2 = np.minimum(x2[i], x2[rest])
        yy2 = np.minimum(y2[i], y2[rest])
        inter = np.maximum(0.0, xx2 - xx1 + 1) * np.maximum(0.0, yy2 - yy1 + 1)
        iou = inter / (areas[i] + areas[rest] - inter)

        order = rest[iou < iou_threshold]
    return keep


def _decode_detections(
    raw_output: np.ndarray,
    input_size: int,
    strides: tuple[int, ...],
    reg_max: int,
    score_threshold: float,
    nms_threshold: float,
) -> list[Detection]:
    """Decode NanoDet-Plus's raw (1, N, 80 + 4*(reg_max+1)) output - per-point
    class scores plus a distribution-focal-loss box regression - into
    Detection objects in the padded input_size x input_size coordinate space."""
    predictions = raw_output[0]
    num_classes = len(COCO_CLASSES)
    center_priors = _generate_center_priors(input_size, strides)

    class_scores = predictions[:, :num_classes]
    best_class = class_scores.argmax(axis=1)
    best_score = class_scores[np.arange(len(predictions)), best_class]

    confident = best_score > score_threshold
    if not np.any(confident):
        return []

    points = center_priors[confident]
    labels = best_class[confident]
    scores = best_score[confident]
    box_dist = predictions[confident, num_classes:]

    centers_x = points[:, 0] * points[:, 2]
    centers_y = points[:, 1] * points[:, 2]

    distances = np.zeros((len(points), 4))
    for side in range(4):
        bin_logits = box_dist[:, side * (reg_max + 1) : (side + 1) * (reg_max + 1)]
        bin_probs = _softmax(bin_logits, axis=1)
        distances[:, side] = (bin_probs * np.arange(reg_max + 1)).sum(axis=1) * points[:, 2]

    x1 = np.clip(centers_x - distances[:, 0], 0, input_size)
    y1 = np.clip(centers_y - distances[:, 1], 0, input_size)
    x2 = np.clip(centers_x + distances[:, 2], 0, input_size)
    y2 = np.clip(centers_y + distances[:, 3], 0, input_size)
    boxes = np.stack([x1, y1, x2, y2], axis=1)

    detections = []
    for label in np.unique(labels):
        mask = labels == label
        keep = _nms(boxes[mask], scores[mask], nms_threshold)
        class_boxes = boxes[mask][keep]
        class_scores_kept = scores[mask][keep]
        for box, score in zip(class_boxes, class_scores_kept):
            detections.append(
                Detection(
                    class_name=COCO_CLASSES[label],
                    confidence=float(score),
                    bbox=(int(round(box[0])), int(round(box[1])), int(round(box[2])), int(round(box[3]))),
                )
            )
    return detections


def _load_session() -> ort.InferenceSession:
    return ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])


def detect_objects(
    image_path: str,
    score_threshold: float = SCORE_THRESHOLD,
    nms_threshold: float = NMS_THRESHOLD,
) -> DetectionResult:
    """All objects NanoDet-Plus finds in the image at image_path, with pixel
    bounding boxes in the *original* image's coordinate space."""
    image_bgr = cv2.imread(image_path)
    height, width = image_bgr.shape[:2]

    padded, scale, pad_x, pad_y = _letterbox(image_bgr, INPUT_SIZE)
    normalized = (padded.astype(np.float32) - NORMALIZE_MEAN) / NORMALIZE_STD
    blob = normalized.transpose(2, 0, 1)[np.newaxis, ...]

    session = _load_session()
    input_name = session.get_inputs()[0].name
    raw_output = session.run(None, {input_name: blob})[0]

    padded_detections = _decode_detections(
        raw_output, INPUT_SIZE, STRIDES, REG_MAX, score_threshold, nms_threshold
    )

    detections = []
    for det in padded_detections:
        x1 = min(width, max(0, (det.bbox[0] - pad_x) / scale))
        y1 = min(height, max(0, (det.bbox[1] - pad_y) / scale))
        x2 = min(width, max(0, (det.bbox[2] - pad_x) / scale))
        y2 = min(height, max(0, (det.bbox[3] - pad_y) / scale))
        detections.append(
            Detection(
                class_name=det.class_name,
                confidence=det.confidence,
                bbox=(int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))),
            )
        )

    return DetectionResult(detections=detections, image_width=width, image_height=height)


def has_object(image_path: str, class_name: str, score_threshold: float = SCORE_THRESHOLD) -> bool:
    """Whether any detection of class_name (a COCO_CLASSES name, e.g. "dog") is present."""
    if class_name not in COCO_CLASSES:
        raise ValueError(f"{class_name!r} is not a COCO class NanoDet-Plus can detect")
    result = detect_objects(image_path, score_threshold=score_threshold)
    return any(det.class_name == class_name for det in result.detections)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "path/to/image.jpg"
    result = detect_objects(path)
    print(f"{path}: {result.image_width}x{result.image_height}")
    for det in result.detections:
        print(f"  {det.class_name} ({det.confidence:.0%}) at {det.bbox}")
