"""Standalone check: is a given image blurry, and by how much (0-100%)?

Usage: python3 -m modules.blur_check <path-to-image>
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

# Placeholder - only used when run with no argument. Pass a real path on the
# command line, or call blur_percent()/is_blurry() directly.
PLACEHOLDER_IMAGE_PATH = "path/to/image.jpg"

# Laplacian variance at/above this is fully sharp (0% blurry); a variance of
# 0 (a perfectly flat image, no edges at all) is 100% blurry. Same
# variance-of-Laplacian technique and default threshold as
# detector/quality.py's detect_blur - confirmed 2026-08-02 as the standard,
# near-zero-cost, non-ML approach for this hardware (see
# documentation/curation/DETECTORS.md).
SHARPNESS_VARIANCE = float(os.environ.get("BLUR_CHECK_SHARPNESS_VARIANCE", "100.0"))


def blur_percent(image_path: str) -> float:
    """How blurry the image at image_path is, from 0.0 (sharp) to 100.0 (very blurry)."""
    image = Image.open(image_path).convert("RGB")
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return float(max(0.0, min(100.0, (1 - variance / SHARPNESS_VARIANCE) * 100)))


def is_blurry(image_path: str) -> bool:
    """True once the image is more blurry than not (blur_percent > 50)."""
    return blur_percent(image_path) > 50.0


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else PLACEHOLDER_IMAGE_PATH
    percent = blur_percent(path)
    verdict = "blurry" if percent > 50.0 else "sharp"
    print(f"{path}: {percent:.1f}% blurry ({verdict})")
