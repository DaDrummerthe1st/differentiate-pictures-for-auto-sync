# Pictures pipeline (three-session plan)

Work tree sketched by Joakim 2026-09-04, each stage its own standalone `modules/` file
(no shared code between stages beyond the database they write to/read from):

1. **`GetListOfValidPictureFiles()`** — walk a folder, filter to valid picture files,
   insert into a `pictures` table: `id (UUID), path, file_metadata (JSON), md5`.
2. **`modules/quality.py`** (built) — blur/exposure/saturation percentages into a
   `quality` table, design in [QUALITY_METRICS.md](QUALITY_METRICS.md).
3. **Prioritize** — process pictures most likely to have detectable objects first.
   Heuristic not yet decided; belongs to session 3's orchestration file, not the
   object detector itself.
4. **`modules/objects.py`** (next session) — object detection, NanoDet-Plus.
5. **`LogScenery()`** — scene/venue classification (beach, indoor/outdoor, woods,
   parking lot...). Already researched in
   [DETECTORS.md](../curation/DETECTORS.md)'s area D ("Scene/venue classification"
   row): no dedicated model, zero-shot classification via the CLIP-family embedding
   (OpenCLIP ViT-B/32, MIT) against text prompts like "a photo of a beach." Status
   there is "researched," not built — not yet scheduled to a specific session.
6. **`OnPicturesWithPeopleDetectedWithProbabilityLimitGroupSamePerson()`** — group
   photos by detected person once face-match probability clears a threshold. Matches
   the clustering approach already designed in
   [IDENTITY_MATCHING.md](../curation/IDENTITY_MATCHING.md) (different naming, same
   underlying mechanism) — not yet reduced to this pipeline's concrete shape.

## Decisions made 2026-09-04

- **SQLite**, not this project's Postgres, for this standalone pipeline — zero-setup,
  fits the Pi-3/1GB-RAM resource constraint, keeps `modules/` fully decoupled per
  Joakim's standing instruction that it never connects to existing code.
- SQLite has no native `ENUM` — use `TEXT` + `CHECK (col IN (...))` instead (e.g.
  `sceneryID`).
- `pictures` is a separate, standalone table — explicitly **not** the same thing as
  the future `photos` catalog table already referenced, undesigned, in
  [tags/SCHEMA.md](../tags/SCHEMA.md).
- `file_metadata` is **filesystem stat data** (`st_mtime`/`st_ctime`/`st_mode`/
  filename — POSIX `stat()`), not EXIF. On Linux, `st_ctime` is metadata-*change*
  time, not creation time — a true creation/birth time exists only on some
  filesystems (`os.statx`, ext4/xfs/btrfs) and needs an explicit decision on whether
  it's worth depending on. EXIF (capture date/GPS/camera, already handled by
  `app/gpsdata.py`) is a separate concern, not folded into this column.
- Object detection model: **NanoDet-Plus (Apache-2.0)**, the already-picked model in
  DETECTORS.md area D — not YOLO. YOLO (AGPL-3.0) is explicitly excluded there for
  the commercial-roadmap conflict (see also [GLOSSARY.md](../GLOSSARY.md)'s AGPL
  entry) — raised and confirmed again this session since the pipeline sketch named
  YOLO specifically.

## Status

Designed 2026-09-04, in conversation. Session 2 (next) builds `modules/objects.py`.
Session 3 builds the orchestration/prioritization file (the `pictures` table, calling
`quality.py` + `objects.py` in priority order). `LogScenery()` and the
group-same-person step are confirmed real but not yet scheduled to a session. See
[TODO.md](TODO.md).
