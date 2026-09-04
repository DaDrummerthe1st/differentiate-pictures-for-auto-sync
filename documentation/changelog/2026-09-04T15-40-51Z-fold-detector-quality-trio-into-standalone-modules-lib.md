# Fold detector quality trio into standalone modules lib

`modules/blur_check.py` renamed to `modules/quality.py` and expanded with `exposure_percent`/`saturation_percent` (TDD: tests written and failing before implementation), per Joakim's request to fold `detector/quality.py`'s full quality trio (blur/exposure/monochrome) into the standalone `modules/` lib — deliberately no shared code with `detector/`, and `modules/` is now framed as a growing detector library, not a one-off script. `documentation/curation/DETECTORS.md` and `documentation/data-modeling/QUALITY_METRICS.md` updated to reflect the implemented state.

- **Doc size**: `documentation/curation/DETECTORS.md` +257 chars; `modules/README.md` +388 chars; `documentation/data-modeling/QUALITY_METRICS.md` +181 chars; `documentation/data-modeling/TODO.md` rewritten, net 0 chars.
