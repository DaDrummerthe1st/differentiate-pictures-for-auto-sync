# Rename quality.py percent functions to check_ prefix

`modules/quality.py`'s `blur_percent`/`exposure_percent`/`saturation_percent` renamed to `check_blur`/`check_exposure`/`check_saturation` (TDD: `modules/tests/test_quality.py` updated to the new names first, confirmed failing, then the rename made it pass). Joakim initially asked for a `Quality` class wrapping these as methods; on reflection a class added no value here (no shared per-instance state, e.g. no image caching across checks) so we kept plain functions instead. Column names in `documentation/data-modeling/QUALITY_METRICS.md`'s design table (`blur_percent` etc.) are unaffected — those name a future DB schema, not this module's functions.

- **Doc size**: `documentation/data-modeling/QUALITY_METRICS.md` -6 chars; `documentation/curation/DETECTORS.md` -4 chars.
