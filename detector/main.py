import io

from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from detector.quality import detect_blur, detect_exposure, detect_monochrome

# Runs the detector models called by the main photo-viewer app, kept in its
# own container so opencv/onnxruntime's footprint never lands in app/'s
# image (documentation/curation/TODO.md's build-plan Phase 1). Face
# detection (YuNet) and object/animal detection (NanoDet-Plus) are Phase
# 3-4, still to come.
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/health")
def health():
    return {"status": "ok"}


def _tag(category: str, value: str) -> dict:
    return {
        "category": category,
        "value": value,
        "bbox_x": None,
        "bbox_y": None,
        "bbox_w": None,
        "bbox_h": None,
    }


@app.post("/detect")
async def detect(file: UploadFile = File(...)) -> dict:
    try:
        image = Image.open(io.BytesIO(await file.read()))
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
    return {"tags": tags}
