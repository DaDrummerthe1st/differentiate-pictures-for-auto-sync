# Vendored model licenses

Fetch-once, commit-once convention (same as `app/static/vendor/`'s jQuery/Bootstrap/Material
Symbols) — models are downloaded from their upstream release, committed here, and never fetched
at build or run time.

## face_detection_yunet_2023mar.onnx

- **Source**: https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx
- **License**: MIT (Shiqi Yu) — the model's own `LICENSE` file in `opencv_zoo`'s
  `models/face_detection_yunet/` directory, not the repo root's Apache-2.0 (the repo root license
  covers `opencv_zoo`'s own code, not each vendored model asset individually; checked directly
  rather than assumed, per documentation/curation/TODO.md's "License-strictness decision"). Still
  within this project's MIT/Apache-2.0-only bar for model weights.
- **SHA-256**: `8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4`
- **Used by**: `detector/faces.py` via `cv2.FaceDetectorYN_create`.
