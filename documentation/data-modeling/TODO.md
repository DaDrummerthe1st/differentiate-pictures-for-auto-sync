# TODO

- No real `file_id`/quality table exists yet — [QUALITY_METRICS.md](QUALITY_METRICS.md)'s column shape stays design-only until `modules/quality.py`'s output is wired into an actual database.
- More detectors are expected to join `modules/` over time (per Joakim) — each stays standalone, no shared code with `detector/` or `app/`.
- [PICTURES_PIPELINE.md](PICTURES_PIPELINE.md): `modules/objects.py` (session 2, NanoDet-Plus) built 2026-09-04. `modules/pictures.py` (session 3, the `pictures`/`locations` register) built 2026-09-04. Still not built: the prioritization heuristic (item 3), wiring `quality.py`/`objects.py` output into the register. `LogScenery()` (scene classification) and the group-same-person step are confirmed real/researched but not yet scheduled to a session.
- `file_metadata`'s birth-time question resolved 2026-09-04: `modules/pictures.py` tries `statx(2)`'s `STATX_BTIME` via `ctypes`, falls back to `birth_time_available=False` (never guessed from `mtime`/`ctime`). Not yet verified against an actual sshfs/NAS mount (only tested on local ext4) — worth a real check once a multi-source scan is exercised for real.
