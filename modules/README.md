# modules/

A standalone detector library — each file its own detector, growing over time. Deliberately no dependency on `detector/`, `app/`, or any other existing code in this repo, even where a detector here covers the same ground as an existing one. See [documentation/curation/DETECTORS.md](../documentation/curation/DETECTORS.md).

- `quality.py` — blur, exposure, and saturation, each 0-100% (or -100 to +100 for exposure). See [documentation/data-modeling/QUALITY_METRICS.md](../documentation/data-modeling/QUALITY_METRICS.md) for the column-shape reasoning.
