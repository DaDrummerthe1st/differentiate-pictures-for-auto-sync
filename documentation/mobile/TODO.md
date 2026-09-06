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
- iOS: still a "consider it, don't build it" note, unchanged.
