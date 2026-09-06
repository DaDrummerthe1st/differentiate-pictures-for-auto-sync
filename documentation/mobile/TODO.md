# mobile/ TODO

- **Confirmed working, 2026-09-06** (see README.md's Status section): builds, installs, shows and
  scrolls all device photos correctly, tap-to-fullscreen works. Decided to keep iterating on the
  current `MainActivity`/`PhotoAdapter`/`FullscreenPhotoActivity` split rather than rewrite —
  Coil now handles image loading/caching/EXIF rotation, with Robolectric unit tests covering the
  adapter and fullscreen activity's own wiring logic.
- **Next up, requested but not yet built**: in `FullscreenPhotoActivity`, add swipe left/right to
  move to the previous/next photo (needs a `ViewPager2` over the photo list, not just a single
  `ImageView`), and pinch-to-zoom/pan on the currently displayed photo (plain `ImageView` has no
  gesture support for this — evaluate a maintained zoomable-image view library rather than
  hand-rolling `Matrix`/`ScaleGestureDetector` code, consistent with the Coil precedent this
  session; check it's actually available via `mavenCentral()`/`google()`, since this project
  doesn't add other repositories like JitPack without discussing it first).
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
