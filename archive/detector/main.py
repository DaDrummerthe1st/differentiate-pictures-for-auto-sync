import io
import os
import resource

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
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


def _cpu_time_ms() -> float:
    # RUSAGE_SELF, not RUSAGE_CHILDREN - this process is
    # synchronous/single-process (no subprocess/worker fan-out), so a
    # before/after delta cleanly attributes CPU time to whichever
    # detect_* call ran between the two reads. See
    # documentation/plans/tingly-humming-pudding.md Part B.
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return (usage.ru_utime + usage.ru_stime) * 1000


@app.post("/detect")
async def detect(file: UploadFile = File(...), include_timing: bool = Query(False)) -> dict:
    body = await _read_capped(file, MAX_UPLOAD_BYTES)
    try:
        image = Image.open(io.BytesIO(body))
        image.load()
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="not a readable image") from exc

    tags = []
    cpu_time_ms = {}

    start = _cpu_time_ms()
    blurry = detect_blur(image)
    cpu_time_ms["blur"] = _cpu_time_ms() - start
    if blurry:
        tags.append(_tag("generic", "blurry"))

    start = _cpu_time_ms()
    exposure = detect_exposure(image)
    cpu_time_ms["exposure"] = _cpu_time_ms() - start
    if exposure is not None:
        tags.append(_tag("generic", exposure))

    start = _cpu_time_ms()
    monochrome = detect_monochrome(image)
    cpu_time_ms["monochrome"] = _cpu_time_ms() - start
    if monochrome:
        tags.append(_tag("generic", "black_and_white"))

    start = _cpu_time_ms()
    faces = detect_faces(image)
    cpu_time_ms["face"] = _cpu_time_ms() - start
    for face in faces:
        tags.append(_tag("people", "Person", face))

    result = {"tags": tags}
    if include_timing:
        # ru_maxrss is a cumulative peak since process start (mostly
        # YuNet's one-time model-load cost), not a per-detector or
        # per-photo cost - report it once per request, labeled batch/
        # request-level, not attributed to any single detector.
        result["timings"] = {
            "cpu_time_ms": cpu_time_ms,
            "peak_rss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        }
    return result
