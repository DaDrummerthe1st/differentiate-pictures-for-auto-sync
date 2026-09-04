# Add standalone modules/blur_check.py percent-based blur prototype

New top-level `modules/` folder holding one standalone, disposable script, `blur_check.py` — reports blur as a 0-100% extent (variance-of-Laplacian, same technique as `detector/quality.py`'s boolean `detect_blur`), deliberately not wired into `detector/` or any other existing code per Joakim's request. TDD: `modules/tests/test_blur_check.py` written and failing before the implementation existed. Sanity-checked against real files in `resources/test_pictures/`.

- **Doc size**: `documentation/curation/DETECTORS.md` +175 chars (noted the new prototype against the existing blur row); new `modules/README.md` stub, 178 chars.
