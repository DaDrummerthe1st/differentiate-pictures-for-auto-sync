# TODO

- No real `file_id`/quality table exists yet — [QUALITY_METRICS.md](QUALITY_METRICS.md)'s column shape stays design-only until `modules/quality.py`'s output is wired into an actual database.
- More detectors are expected to join `modules/` over time (per Joakim) — each stays standalone, no shared code with `detector/` or `app/`.
