# Update DETECTORS.md: mark object/animal detection built, fix broken EXIF link

Joakim asked for a deterministic re-check of a detection-features summary against DETECTORS.md's
literal text. Audit caught the source doc itself was stale: object detection and animal
coarse-species rows still said "researched" though modules/objects.py shipped this session, and
the EXIF/GPS row's link still pointed at prototypes/... at the repo root - broken since that
tree moved under archive/ and was never repointed. All three fixed in place.

- **Doc size**: DETECTORS.md +484.
