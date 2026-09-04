import os

import cv2
import numpy as np
from PIL import Image

# Overridable via env, never hardcoded past this point - see
# documentation/curation/TODO.md's build plan, Phase 2.
BLUR_VARIANCE_THRESHOLD = float(os.environ.get("QUALITY_BLUR_VARIANCE_THRESHOLD", "100.0"))
UNDEREXPOSED_MEAN_LUMINANCE = float(os.environ.get("QUALITY_UNDEREXPOSED_MEAN_LUMINANCE", "40.0"))
OVEREXPOSED_MEAN_LUMINANCE = float(os.environ.get("QUALITY_OVEREXPOSED_MEAN_LUMINANCE", "215.0"))
MONOCHROME_SATURATION_THRESHOLD = float(
    os.environ.get("QUALITY_MONOCHROME_SATURATION_THRESHOLD", "15.0")
)


def _grayscale_array(image: Image.Image) -> np.ndarray:
    bgr = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)


def detect_blur(image: Image.Image) -> bool:
    variance = cv2.Laplacian(_grayscale_array(image), cv2.CV_64F).var()
    return bool(variance < BLUR_VARIANCE_THRESHOLD)


def detect_exposure(image: Image.Image) -> str | None:
    mean_luminance = float(_grayscale_array(image).mean())
    if mean_luminance <= UNDEREXPOSED_MEAN_LUMINANCE:
        return "underexposed"
    if mean_luminance >= OVEREXPOSED_MEAN_LUMINANCE:
        return "overexposed"
    return None


def detect_monochrome(image: Image.Image) -> bool:
    bgr = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mean_saturation = float(hsv[:, :, 1].mean())
    return bool(mean_saturation < MONOCHROME_SATURATION_THRESHOLD)
