# mobile/ TODO

- **Confirmed working, 2026-09-06** (see README.md's Status section): builds, installs, shows and
  scrolls all device photos correctly, tap-to-fullscreen works. Decided to keep iterating on the
  current `MainActivity`/`PhotoAdapter`/`FullscreenPhotoActivity` split rather than rewrite —
  Coil now handles image loading/caching/EXIF rotation, with Robolectric unit tests covering the
  adapter and fullscreen activity's own wiring logic.
- **Built 2026-09-06, needs Joakim's manual gesture check**: `FullscreenPhotoActivity` now uses a
  `ViewPager2` (backed by a new `FullscreenPhotoPagerAdapter`) instead of a single `ImageView`, so
  swiping left/right moves to the previous/next photo across the whole grid, not just the one
  tapped. Each page is an `io.getstream.photoview.PhotoView` (Maven Central, Stream's fork of
  `chrisbanes/PhotoView` — **corrected 2026-09-06, dependency audit**: the original wasn't
  GitHub-archived, it was transferred to `Baseflow/PhotoView` and has had no commit since
  2022-03-25; Stream's own fork is maintained-but-dormant on actual library code too — CI/tooling
  commits continue, but no functional release since 1.0.3 on 2025-02-13 — the least-stale of the
  realistic options, not a clean "actively maintained" story; see
  [security/DEPENDENCIES.md](../security/DEPENDENCIES.md)), chosen over the also-Maven-Central but
  unmaintained-since-2021 `com.jsibbold:zoomage` — see
  [GLOSSARY.md](../GLOSSARY.md)) for pinch-to-zoom/pan, since `PhotoView` is a drop-in `ImageView`
  subclass Coil loads into exactly like before. Covered by Robolectric tests for the wiring
  (`FullscreenPhotoActivityTest`, `FullscreenPhotoPagerAdapterTest`) but the actual swipe/pinch/pan
  *feel* needs a real touchscreen gesture — confirmed via adb/logcat that swiping between photos
  works with no crash, but pinch-zoom itself is unverified pending Joakim checking it by hand on
  the emulator — an AI session verifies app behavior via logs/adb text output, never screenshots;
  actual visual/gesture checks are Joakim's to do and report back.
- **Known, accepted non-issue**: Coil's in-memory thumbnail cache gets evicted under real memory
  pressure (this dev machine runs Gradle + the emulator simultaneously, which is unusually heavy;
  a real phone would see this far less) — falls back to its disk cache (fast, not instant) rather
  than a full re-decode. Joakim explicitly accepted this as fine; don't "fix" it without cause.
- **Resume the deferred roadmap once swipe/zoom is settled**: on-device quality scoring (port of
  `previous-work/pictures-pipeline/quality.py`), on-device object detection (port of
  `objects.py`), user-driven sync to a server, automatic background trigger. None of this is
  scoped yet — treat `previous-work/pictures-pipeline/` as reference only, not a plan to resume
  verbatim, per [../../previous-work/README.md](../../previous-work/README.md).
- iOS: still a "consider it, don't build it" note, unchanged.
