# Face detection (YuNet) built for the detector service

Phase 3 of the automatic-tagging build plan (`documentation/curation/TODO.md`): `detector/faces.py`
wraps `cv2.FaceDetectorYN` over a vendored `detector/models/face_detection_yunet_2023mar.onnx`
(OpenCV Zoo), wired into `POST /detect` alongside the quality trio, TDD'd against real fixtures from
`resources/test_pictures/Florida1/`. Caught and fixed one real gap mid-build: YuNet's native output
is pixel coordinates, but `app/main.py`'s tag storage requires normalized `0..1` fractions of image
width/height — `detect_faces` now clamps to image bounds and normalizes before returning, confirmed
against `_validate_tag_fields`'s actual checks rather than assumed. Also corrected the model's license
in docs: MIT (its own `LICENSE` file), not the `opencv_zoo` repo root's Apache-2.0 — both are within
this project's license bar, so no functional change, just an accuracy fix.

- **Doc size**: `documentation/curation/TODO.md` +2505 chars.
- **Doc size**: `documentation/GLOSSARY.md` +719 chars.
- **Doc size**: `documentation/tags/SCHEMA.md` +440 chars.
- **Doc size**: `documentation/curation/DETECTORS.md` +405 chars.
