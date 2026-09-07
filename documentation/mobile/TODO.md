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
- **Open design question, raised 2026-09-07, not addressed anywhere in `curation/` yet**: can the
  on-device suggestion/scoring logic get stuck when a photo scores equally under two competing
  signals (e.g. "keep" and "delete" candidates tie)? Logged as new, unresolved — see
  [../curation/TODO.md](../curation/TODO.md)'s matching entry.
- iOS: still a "consider it, don't build it" note, unchanged.
