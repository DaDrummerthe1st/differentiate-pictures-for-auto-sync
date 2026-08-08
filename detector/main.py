import io
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from detector.faces import detect_faces
from detector.quality import detect_blur, detect_exposure, detect_monochrome

# Runs the detector models called by the main photo-viewer app, kept in its
# own container so opencv/onnxruntime's footprint never lands in app/'s
# image (documentation/curation/TODO.md's build-plan Phase 1). Object/animal
# detection (NanoDet-Plus) is Phase 4, still to come.
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Resource-exhaustion guard (documentation/security/THREATS.md #16) -
# generous headroom over real photo file sizes, overridable via env.
MAX_UPLOAD_BYTES = int(os.environ.get("DETECT_MAX_UPLOAD_BYTES", str(25 * 1024 * 1024)))
_UPLOAD_READ_CHUNK_BYTES = 1024 * 1024


async def _read_capped(file: UploadFile, max_bytes: int) -> bytes:
    chunks = []
    total = 0
    while True:
        chunk = await file.read(_UPLOAD_READ_CHUNK_BYTES)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(status_code=413, detail="file too large")
        chunks.append(chunk)
    return b"".join(chunks)


@app.get("/health")
def health():
    return {"status": "ok"}


def _tag(category: str, value: str, bbox: dict | None = None) -> dict:
    bbox = bbox or {}
    return {
        "category": category,
        "value": value,
        "bbox_x": bbox.get("bbox_x"),
        "bbox_y": bbox.get("bbox_y"),
        "bbox_w": bbox.get("bbox_w"),
        "bbox_h": bbox.get("bbox_h"),
    }


@app.post("/detect")
async def detect(file: UploadFile = File(...)) -> dict:
    body = await _read_capped(file, MAX_UPLOAD_BYTES)
    try:
        image = Image.open(io.BytesIO(body))
        image.load()
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="not a readable image") from exc

    tags = []
    if detect_blur(image):
        tags.append(_tag("generic", "blurry"))
    exposure = detect_exposure(image)
    if exposure is not None:
        tags.append(_tag("generic", exposure))
    if detect_monochrome(image):
        tags.append(_tag("generic", "black_and_white"))
    for face in detect_faces(image):
        tags.append(_tag("people", "Person", face))
    return {"tags": tags}
