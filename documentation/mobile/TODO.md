# mobile/ TODO

- **Confirmed working, 2026-09-06** (see README.md's Status section): builds, installs, shows and
  scrolls all device photos correctly, tap-to-fullscreen works. Decided to keep iterating on the
  current `MainActivity`/`PhotoAdapter`/`FullscreenPhotoActivity` split rather than rewrite —
  Coil now handles image loading/caching/EXIF rotation, with Robolectric unit tests covering the
  adapter and fullscreen activity's own wiring logic.
- **Confirmed working, 2026-09-06**: `FullscreenPhotoActivity` now uses a `ViewPager2` (backed by
  a new `FullscreenPhotoPagerAdapter`) instead of a single `ImageView`, so swiping left/right moves
  to the previous/next photo across the whole grid, not just the one tapped. Each page is an
  `io.getstream.photoview.PhotoView` (Maven Central, actively-maintained fork of the abandoned
  `chrisbanes/PhotoView`, chosen over the also-Maven-Central but unmaintained-since-2021
  `com.jsibbold:zoomage` — see [GLOSSARY.md](../GLOSSARY.md)) for pinch-to-zoom/pan, since
  `PhotoView` is a drop-in `ImageView` subclass Coil loads into exactly like before. Covered by
  Robolectric tests for the wiring (`FullscreenPhotoActivityTest`,
  `FullscreenPhotoPagerAdapterTest`); swipe and pinch-zoom-in both confirmed by Joakim manually on
  the emulator (see [GLOSSARY.md](../GLOSSARY.md) for how to simulate pinch with the mouse).
  **Known, accepted non-issue**: `PhotoView`'s default minimum scale is the fit-to-screen size, so
  pinching back out never shrinks the photo smaller than its original display size — Joakim
  confirmed this is fine, no need to zoom below original size.
- **Known, accepted non-issue**: Coil's in-memory thumbnail cache gets evicted under real memory
  pressure (this dev machine runs Gradle + the emulator simultaneously, which is unusually heavy;
  a real phone would see this far less) — falls back to its disk cache (fast, not instant) rather
  than a full re-decode. Joakim explicitly accepted this as fine; don't "fix" it without cause.
- **Resume the deferred roadmap once swipe/zoom is settled**: on-device quality scoring (port of
  `previous-work/pictures-pipeline/quality.py`), on-device object detection (port of
  `objects.py`), user-driven sync to a server, automatic background trigger. None of this is
  scoped yet — treat `previous-work/pictures-pipeline/` as reference only, not a plan to resume
  verbatim, per [../../previous-work/README.md](../../previous-work/README.md).
- **On-device storage — architecture decided, nothing built, 2026-09-07**: the app has no local
  database at all today, just a live `MediaStore` query. Once it needs to save anything (quality/
  object-detection output, an event log of what the user does with a photo), the pick is **Room**
  (Jetpack's SQLite wrapper) over `DataStore` (key-value only, wrong shape for per-photo/relational
  data) or plain files (can't query across records). Shape to build: a log-then-recompute pattern,
  not stable stored counters — same as [../curation/GAMIFICATION.md](../curation/GAMIFICATION.md)'s
  server-side `audit_log` reuse, just moved on-device: a local events table
  (`photo_id, action, details, created_at`), with any score (usage-intent, future confidence tally)
  recomputed from it at read time, never a separately-maintained counter that can drift.
- **Future feature work (object detection, contacts linking, environment/scene detection,
  gamified confidence display) is mostly already designed, not blank** — see
  [../curation/README.md](../curation/README.md)'s 2026-09-06 note: `curation/` was written
  assuming server-side inference, before this app existed. `DETECTORS.md` area D already has
  object detection **built** (`modules/objects.py`, NanoDet-Plus) and scene/venue classification
  (beach, indoor/outdoor, etc.) **researched** (zero-shot CLIP against text prompts, no new model).
  `IDENTITY_MATCHING.md` already has usage-intent scoring (the "why did the user do X" question)
  and CardDAV contacts-linking research done, build deferred. `GAMIFICATION.md` is a full spec for
  the credit/confidence-display mechanic. The real work porting any of this on-device is schema/
  runtime porting (Room instead of Postgres, on-device ONNX Runtime for Android instead of a
  server-side Python process), not fresh design — when that porting actually happens, flag any
  place it deviates from a `curation/` doc's server-side assumption inline in that doc, same
  convention already used elsewhere (e.g. `curation/IDENTITY_MATCHING.md`'s "Reversed 2026-09-05"
  note), rather than silently diverging.
- **On-device runtime pick — researched 2026-09-07, not yet decided**: `com.microsoft.onnxruntime:onnxruntime-android` (Maven Central, MIT, currently 1.27.0) is the direct on-device counterpart to the server-side picks (same `.onnx` files, NNAPI/XNNPACK hardware acceleration on Android). Two real mobile-purpose-built alternatives exist that also consume ONNX models (via import/conversion, not direct execution): **ncnn** (Tencent, BSD-3-Clause, lighter footprint, NanoDet-Plus's own official repo ships an ncnn deployment path specifically) and **MNN** (Alibaba, Apache-2.0). Correction to an initial framing: neither is meaningfully "more open source" than ONNX Runtime — all three are single-company-led OSS with similarly permissive licenses; the real trade-off is mobile-optimized footprint/speed vs. ONNX Runtime's broader format compatibility and reuse of the exact same server-side model files with zero conversion step. Not decided — worth a real footprint/speed comparison once object-detection porting actually starts.
- **Open design question, raised 2026-09-07, not addressed anywhere in `curation/` yet**: can the
  on-device suggestion/scoring logic get stuck when a photo scores equally under two competing
  signals (e.g. "keep" and "delete" candidates tie)? Logged as new, unresolved — see
  [../curation/TODO.md](../curation/TODO.md)'s matching entry.
- **Backlog raised 2026-09-07, none designed or scoped yet** (deliberately logged, not built: a
  second AI session was concurrently active on this same branch/checkout at the time, with no
  worktree isolation between them, so building blind risked a real file collision — and the list
  itself was too large for one session regardless):
  - **Swipe-to-triage gesture** — design discussion started 2026-09-07, see
    [UX_FLOWS.md](UX_FLOWS.md): a two-way swipe (remove-from-view vs. organize/tag), a two-tier
    recoverability model (immediate undo + a durable, never-auto-purged-by-default "Removed" bin)
    satisfying Joakim's hard always-recoverable rule. Awaiting his confirmation on the left/right
    direction mapping before this is build-ready.
  - **Bounding boxes surfaced in the grid view itself**, not just the fullscreen view, once
    object detection is on-device — needs a concrete visual treatment, not just "draw a box."
  - **Sort/order control**, user-chosen, always available — not a fixed default ordering.
  - **Folder-usage-frequency signal** — track which folders/albums get used more, no concrete use
    identified yet, logged as a hint for future visualization decisions.
  - **Storage-transparency dashboard**: total storage used across device/NAS/cloud/paid tiers,
    shown plainly so the user stays in control of what to delete and where — explicitly positioned
    against services that obscure this to keep usage growing. Central to why deletion-focused
    curation works at all (seeing the real number is what makes "delete more" feel possible).
  - **Confidence-score-driven NAS request flow** (depends on the NAS/backup-sync work below): once
    a NAS exists, it computes a confidence score per photo and requests upload of specifically the
    photos it's least confident about, rather than the phone pushing everything. A file present on
    both phone and NAS independently needs to be flagged/reconciled, not treated as two unrelated
    copies.
  - **NAS/backup-sync structure — recommended as its own session, own branch, own worktree**: a
    genuinely separate subsystem (targets `192.168.1.10` directly, no expensive SSD/RPi storage
    needed) with no file overlap with `android/`, so it's also the cleanest fix for this session's
    concurrent-editing concern — a different worktree means a different directory, not just a
    different branch checked out in the same one.
- iOS: still a "consider it, don't build it" note, unchanged.
