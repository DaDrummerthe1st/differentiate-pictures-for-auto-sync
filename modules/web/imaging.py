"""Image bytes for modules/web/server.py's /image/<location_id> endpoint:
a plain scaled-down thumbnail for the grid view, or (via modules.findings.annotate)
a full-size photo with detection boxes drawn on it for the per-picture detail view.
"""
import io

from PIL import Image, ImageOps

JPEG_QUALITY = 85


def thumbnail(image_path: str, max_size: int) -> Image.Image:
    """image_path scaled down to fit within max_size x max_size, preserving
    aspect ratio; left unscaled if it's already smaller than that."""
    image = ImageOps.exif_transpose(Image.open(image_path)).convert("RGB")
    scale = min(1.0, max_size / max(image.width, image.height))
    if scale < 1.0:
        image = image.resize((round(image.width * scale), round(image.height * scale)))
    return image


def encode_jpeg(image: Image.Image, quality: int = JPEG_QUALITY) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()
