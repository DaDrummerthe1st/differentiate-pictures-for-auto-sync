# data-modeling/

Cross-cutting: table/column shapes and naming decisions worked out in conversation, for standalone or exploratory data that doesn't yet belong to one of the built schemas ([tags/SCHEMA.md](../tags/SCHEMA.md), [photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md)). Not a replacement for those — once a design here is ready to join a real table, it moves there instead of living in two places.

| File | What's there |
| --- | --- |
| [QUALITY_METRICS.md](QUALITY_METRICS.md) | Column shape/naming for a per-photo quality-percent table (blur/exposure/saturation) — the design behind [modules/quality.py](../../modules/quality.py) |
| [PICTURES_PIPELINE.md](PICTURES_PIPELINE.md) | The multi-session `modules/` pipeline (file discovery → quality → object detection → scene classification → person grouping), SQLite vs. Postgres, `file_metadata` vs. EXIF |
