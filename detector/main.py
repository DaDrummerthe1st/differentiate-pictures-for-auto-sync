from fastapi import FastAPI

# Skeleton only, this session (documentation/curation/TODO.md's build-plan
# Phase 0/1) - runs the detector models called by the main photo-viewer
# app, kept in its own container so opencv/onnxruntime's footprint never
# lands in app/'s image. No detection endpoint yet: the quality trio
# (blur/exposure/monochrome), face detection (YuNet), and object/animal
# detection (NanoDet-Plus) are the next session's Phase 2-4, per the
# handoff note in documentation/curation/TODO.md.
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/health")
def health():
    return {"status": "ok"}
