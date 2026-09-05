"""EXIF reading and detection-annotation, shared by every dev tool that
displays a photo alongside its modules/ findings (modules/test_main.py, the
web viewer in modules/web/). Self-contained - no dependency on detector/,
app/, or any other existing code in this repo, same pattern as
modules/quality.py and modules/objects.py.
"""
from PIL import ExifTags, Image, ImageDraw, ImageOps

from modules.objects import DetectionResult

BOX_COLOR = "red"


def format_exposure_time(seconds: float) -> str:
    return f"{seconds:.1f}s" if seconds >= 1 else f"1/{round(1 / seconds)}s"


def gps_to_decimal(dms: tuple | None, ref: str | None) -> float | None:
    if not dms or not ref:
        return None
    degrees, minutes, seconds = dms
    decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    return -decimal if ref in ("S", "W") else decimal


def exif_lines(image_path: str) -> list[str]:
    """Every commonly-useful EXIF field this photo actually has - camera,
    capture settings, capture date, GPS - as plain-language lines."""
    exif = Image.open(image_path).getexif()
    if not exif:
        return ["(none)"]

    base = {ExifTags.TAGS.get(tag_id, tag_id): value for tag_id, value in exif.items()}
    try:
        sub = {ExifTags.TAGS.get(tag_id, tag_id): value for tag_id, value in exif.get_ifd(ExifTags.IFD.Exif).items()}
    except Exception:
        sub = {}

    lines = []
    if "Make" in base or "Model" in base:
        lines.append(f"Camera: {base.get('Make', '')} {base.get('Model', '')}".strip())
    if "DateTimeOriginal" in sub:
        lines.append(f"Captured: {sub['DateTimeOriginal']}")
    settings = []
    if "ExposureTime" in sub:
        settings.append(format_exposure_time(sub["ExposureTime"]))
    if "FNumber" in sub:
        settings.append(f"f/{sub['FNumber']}")
    if "ISOSpeedRatings" in sub:
        settings.append(f"ISO {sub['ISOSpeedRatings']}")
    if "FocalLength" in sub:
        settings.append(f"{sub['FocalLength']}mm")
    if settings:
        lines.append("Settings: " + "  ".join(settings))

    try:
        gps = exif.get_ifd(ExifTags.IFD.GPSInfo)
        lat = gps_to_decimal(gps.get(2), gps.get(1))
        lon = gps_to_decimal(gps.get(4), gps.get(3))
        if lat is not None and lon is not None:
            lines.append(f"GPS: {lat:.6f}, {lon:.6f}")
    except Exception:
        pass

    return lines or ["(none)"]


def annotate(
    image_path: str, result: DetectionResult, max_display_width: int = 900, box_color: str = BOX_COLOR
) -> Image.Image:
    """The photo, resized to fit within max_display_width, with every
    detection's bounding box and label drawn on top."""
    # cv2.imread (modules/objects.py's detector) auto-rotates a JPEG per its
    # EXIF orientation tag, so detect_objects()'s bboxes are in that rotated,
    # upright coordinate space - PIL.Image.open does *not* auto-rotate, so
    # this must match that rotation explicitly or boxes land on the wrong
    # content entirely (found 2026-09-04: correct predictions, wrong places).
    image = ImageOps.exif_transpose(Image.open(image_path)).convert("RGB")
    assert (image.width, image.height) == (result.image_width, result.image_height), (
        f"annotated image size {image.size} doesn't match detection's "
        f"({result.image_width}, {result.image_height}) - EXIF rotation mismatch"
    )
    scale = min(1.0, max_display_width / image.width)
    if scale < 1.0:
        image = image.resize((round(image.width * scale), round(image.height * scale)))

    draw = ImageDraw.Draw(image)
    for det in result.detections:
        x1, y1, x2, y2 = (round(v * scale) for v in det.bbox)
        draw.rectangle((x1, y1, x2, y2), outline=box_color, width=2)
        label = f"{det.class_name} {det.confidence:.0%}"
        label_y = max(0, y1 - 14)
        draw.rectangle((x1, label_y, x1 + 7 * len(label), label_y + 14), fill=box_color)
        draw.text((x1 + 2, label_y + 1), label, fill="white")
    return image
