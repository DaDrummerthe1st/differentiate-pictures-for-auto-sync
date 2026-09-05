# Pictures pipeline (three-session plan)

Work tree sketched by Joakim 2026-09-04, each stage its own standalone `modules/` file
(no shared code between stages beyond the database they write to/read from):

1. **`GetListOfValidPictureFiles()`** (built 2026-09-04) — walk a folder, filter to valid
   picture files, register into a two-table SQLite register: `pictures` (`id (UUID), md5
   (UNIQUE), first_registered_at`) and `locations` (`id (UUID), picture_id, path (UNIQUE),
   source, file_metadata (JSON), first_seen_at, last_seen_at`) — see "Decisions made
   2026-09-04 (session 3)" below for why path/file_metadata moved out of `pictures` into a
   separate table.
2. **`modules/quality.py`** (built) — blur/exposure/saturation percentages into a
   `quality` table, design in [QUALITY_METRICS.md](QUALITY_METRICS.md).
3. **Prioritize** — process pictures most likely to have detectable objects first.
   Heuristic not yet decided; belongs to session 3's orchestration file, not the
   object detector itself.
4. **`modules/objects.py`** (built 2026-09-04) — object detection, NanoDet-Plus. `detect_objects()`
   returns a combined `DetectionResult` (all detections + image width/height); `has_object()` is a
   per-class convenience wrapper. Bounding boxes are pixel coordinates, not normalized — see
   [GLOSSARY.md](../GLOSSARY.md)'s bounding-box entry for why this deliberately diverges from the
   archived GUI's normalized-fraction convention.
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

## Decisions made 2026-09-04 (session 2, `modules/objects.py` build)

- **Model confirmed, not just carried forward on faith**: this session's own restart
  instructions explicitly required re-confirming NanoDet-Plus rather than assuming the prior
  pick still applied — asked again, Joakim confirmed it.
- **Vendored `modules/models/nanodet-plus-m_416.onnx`**: Apache-2.0, downloaded from the
  upstream repo's own GitHub release, license checked directly against the repo's own
  `LICENSE` file (see `modules/models/LICENSES.md`).
- **Combined-object shape, richer than `quality.py`'s bare floats**: `detect_objects()` returns
  one `DetectionResult` (a list of `Detection(class_name, confidence, bbox)` plus image
  width/height) rather than one function per class. `quality.py` retrofitted the same day with
  a `check_all()` bundling its three existing bare-float checks into one `QualityResult`, per
  Joakim's explicit ask that every `modules/` detector expose a combined view, not just this
  new one.
- **Bounding boxes are pixel coordinates**, not normalized 0..1 fractions — chosen specifically
  so a later detector can crop straight to the box (`image.crop((x1, y1, x2, y2))`) with no
  re-multiplication step. Diverges from the archived GUI's normalized convention on purpose;
  see [GLOSSARY.md](../GLOSSARY.md).
- **Preprocessing gotcha found empirically**: the plain ONNX release does not bake in input
  normalization (unlike the repo's own OpenVINO IR demo, which has it folded in via
  model-optimizer flags) — feeding raw pixels produced confidently wrong detections (e.g.
  "parking meter" at 100% on a bus photo). Fixed by applying the BGR mean/std from the
  upstream training config (`modules/models/LICENSES.md` has the exact values and the
  before/after evidence).
- **Testing without pip/network mid-session**: turned out to be a non-issue — this repo's
  `.venv-test` already has `onnxruntime`, `cv2`, `numpy`, `PIL`, and `tkinter` installed, and
  outbound network access works, so real inference was tested directly (no fixture-photo or
  model-mocking workaround needed for that part). `modules/tests/test_objects.py` still mocks
  the ONNX forward pass for fast/deterministic pytest runs; `modules/test_main.py` (a tkinter
  folder-picker + results window, not a pytest test) is the manual real-model verification
  tool for local dev use.

## Decisions made 2026-09-04 (session 3, `modules/pictures.py` build)

- **One picture, many locations — confirmed by Joakim**: the same photo (same MD5) found again
  at a different path (moved, re-mounted, copied to a second drive) is the *same* picture with
  an additional recorded location, not a new entry. Drove the schema split: `pictures` is keyed
  by MD5 alone; `path` and `file_metadata` moved to a separate `locations` table, since
  filesystem stat data is inherently per-location anyway (the same photo can have different
  mtimes/inodes at different paths) — this wasn't just a dedup preference, it changed the shape
  of the original one-table sketch above.
- **Incremental rescans, confirmed**: re-scanning a source skips a path already registered with
  unchanged size/mtime (no re-hash). A changed path is re-hashed; if its MD5 changed too, the
  location is repointed at the right `pictures` row (creating one if the new content is
  genuinely new), rather than treating a same-path content change as a brand-new location.
- **`file_metadata`'s birth-time question, resolved**: try `statx(2)`'s `STATX_BTIME` (via
  `ctypes` — Python's `os.stat()` never exposes a birth time on Linux, only macOS/BSD do) and
  register the finding as two always-present keys, `birth_time` (nullable) and
  `birth_time_available` (bool) — never silently fall back into `mtime`/`ctime` without saying
  so. Verified empirically against this session's own ext4 dev filesystem: `statx` succeeds and
  returns a real birth time. Expected to report `birth_time_available=False` on sshfs/NAS mounts
  (not independently verified this session, no such mount available to test against) — the
  fallback path exists specifically for that multi-source case.
- **DB location**: `databases/app.db` at the project root, gitignored — it indexes real personal
  photo metadata, never committed. Named `app.db` rather than `pictures.db` (renamed 2026-09-05)
  since `contacts/db.py` shares this same file for its `contacts`/`contact_emails` tables — see
  [contacts/README.md](../../contacts/README.md).
- **Out of scope, confirmed**: wiring `quality.py`/`objects.py` output into this register, and
  the prioritization heuristic (this file's item 3) are both later, separate passes — this
  session built only the register itself.

## Status

Designed 2026-09-04, in conversation. **Session 2 done same day**: `modules/objects.py` built,
tested (12 unit tests + 2 real-photo smoke tests), and `quality.py` retrofitted with
`check_all()`. **Session 3 done same day**: `modules/pictures.py` built and tested (15 unit
tests, all passing) — `GetListOfValidPictureFiles()`, the `pictures`/`locations` register
described above. Wiring `quality.py`/`objects.py` output into the register, the prioritization
heuristic (item 3), `LogScenery()`, and the group-same-person step remain unbuilt. See
[TODO.md](TODO.md).
