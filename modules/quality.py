"""Standalone photo-quality checks: blur, exposure, and saturation, each as a
percentage. Self-contained - no dependency on detector/ or any other existing
code in this repo, by design (more detectors are meant to join modules/ the
same way, independently).

Usage: python3 -m modules.quality <path-to-image>
"""
import os
import sys
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

# Placeholder - only used when run with no argument. Pass a real path on the
# command line, or call the functions below directly.
PLACEHOLDER_IMAGE_PATH = "path/to/image.jpg"

# Laplacian variance at/above this is fully sharp (0% blurry); a variance of
# 0 (a perfectly flat image, no edges at all) is 100% blurry. Same
# variance-of-Laplacian technique and default threshold researched
# 2026-08-02 as the standard, near-zero-cost, non-ML approach for this
# hardware (see documentation/curation/DETECTORS.md).
SHARPNESS_VARIANCE = float(os.environ.get("QUALITY_SHARPNESS_VARIANCE", "100.0"))


def _rgb_array(image_path: str) -> np.ndarray:
    return np.array(Image.open(image_path).convert("RGB"))


def check_blur(image_path: str) -> float:
    """How blurry the image at image_path is, from 0.0 (sharp) to 100.0 (very blurry)."""
    gray = cv2.cvtColor(_rgb_array(image_path), cv2.COLOR_RGB2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return float(max(0.0, min(100.0, (1 - variance / SHARPNESS_VARIANCE) * 100)))


def is_blurry(image_path: str) -> bool:
    """True once the image is more blurry than not (check_blur > 50)."""
    return check_blur(image_path) > 50.0


def check_exposure(image_path: str) -> float:
    """Exposure balance, from -100.0 (fully black) to +100.0 (fully white), 0 = balanced.

    Mirrors camera exposure-compensation (EV) convention: negative is
    underexposed, positive is overexposed.
    """
    gray = cv2.cvtColor(_rgb_array(image_path), cv2.COLOR_RGB2GRAY)
    mean_luminance = float(gray.mean())  # 0-255, 127.5 = balanced midpoint
    deviation = (mean_luminance - 127.5) / 127.5 * 100
    return float(max(-100.0, min(100.0, deviation)))


def check_saturation(image_path: str) -> float:
    """How colorful the image is, from 0.0 (grayscale) to 100.0 (fully saturated)."""
    hsv = cv2.cvtColor(_rgb_array(image_path), cv2.COLOR_RGB2HSV)
    mean_saturation = float(hsv[:, :, 1].mean())  # 0-255
    return float(max(0.0, min(100.0, mean_saturation / 255 * 100)))


@dataclass(frozen=True)
class QualityResult:
    blur: float
    exposure: float
    saturation: float


def check_all(image_path: str) -> QualityResult:
    """Every quality check for image_path, run once each, bundled together."""
    return QualityResult(
        blur=check_blur(image_path),
        exposure=check_exposure(image_path),
        saturation=check_saturation(image_path),
    )


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else PLACEHOLDER_IMAGE_PATH
    blur = check_blur(path)
    exposure = check_exposure(path)
    saturation = check_saturation(path)
    print(f"{path}:")
    print(f"  blur: {blur:.1f}% ({'blurry' if blur > 50.0 else 'sharp'})")
    print(f"  exposure: {exposure:+.1f}% ({'balanced' if abs(exposure) < 20.0 else ('overexposed' if exposure > 0 else 'underexposed')})")
    print(f"  saturation: {saturation:.1f}% ({'colorful' if saturation > 50.0 else 'grayscale'})")
