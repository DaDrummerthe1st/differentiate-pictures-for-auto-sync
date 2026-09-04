# TODO

- No real `file_id`/quality table exists yet — [QUALITY_METRICS.md](QUALITY_METRICS.md)'s column shape stays design-only until `modules/quality.py`'s output is wired into an actual database.
- More detectors are expected to join `modules/` over time (per Joakim) — each stays standalone, no shared code with `detector/` or `app/`.
- [PICTURES_PIPELINE.md](PICTURES_PIPELINE.md): `modules/objects.py` (session 2, NanoDet-Plus) not yet built. Session 3's orchestration file (the `pictures` table, prioritization heuristic) not yet built. `LogScenery()` (scene classification) and the group-same-person step are confirmed real/researched but not yet scheduled to a session.
- Decide whether `file_metadata` needs true filesystem birth time (`os.statx`, only available on some filesystems) or `st_mtime`/`st_ctime` are sufficient.
