# kotlin/

The native Android photo-browser app — sideloaded only, no Google Play — built 2026-09-06 (was
`android/` at the repo root, on the `android-app-test1` branch). Archived here the same day when
Joakim decided to build the client in React instead, starting fresh next session — full
background/reasoning: [documentation/VISION.md](../../documentation/VISION.md)'s 2026-09-06 note.
Same convention as this directory's other subprojects: disregarded as code, reference and
inspiration only — nothing here runs, no test suite gates commits against it. The UI/UX goals it
reached (photo grid, tap-to-fullscreen, swipe, pinch-to-zoom) are still the target; ask before
assuming any specific implementation choice below (library pick, Gradle/Kotlin toolchain version,
TDD pattern) carries forward into the React rebuild rather than being re-derived fresh.

## What's here

- `app/src/main/java/com/dpfas/photobrowser/MainActivity.kt` — requests photo access
  (`READ_MEDIA_IMAGES`/`READ_EXTERNAL_STORAGE`), queries `MediaStore` on a background thread for
  every device photo, shows them in a `GridView`, wires tap-to-fullscreen.
- `PhotoAdapter.kt` — the `GridView`'s adapter; delegates thumbnail loading/caching/EXIF rotation
  to [Coil](https://coil-kt.github.io/coil/) via an injectable `loadImage` lambda. A fixed decode
  size plus `Precision.INEXACT` keeps Coil's memory-cache key stable despite `GridView`'s view
  recycling (a larger already-cached bitmap, e.g. from viewing the same photo fullscreen, still
  counts as a hit) — see the file's own comments for the full reasoning, confirmed via Coil's
  `DebugLogger`.
- `FullscreenPhotoActivity.kt` / `FullscreenPhotoPagerAdapter.kt` — a swipeable (`ViewPager2`)
  fullscreen view across the whole photo list rather than just the tapped photo, each page an
  `io.getstream.photoview.PhotoView` (Maven Central, maintained fork of the abandoned
  `chrisbanes/PhotoView`, chosen over the also-Maven-Central but unmaintained-since-2021
  `com.jsibbold:zoomage`) for pinch-to-zoom/pan.
- `PhotoBrowserApplication.kt` — configures Coil's singleton `ImageLoader` (debug-only logging via
  `BuildConfig.DEBUG`).
- `app/src/test/` — Robolectric unit tests for the adapter/activity wiring logic, via the same
  injectable-seam pattern as `PhotoAdapter`'s `loadImage` lambda, rather than exercising Coil's or
  `PhotoView`'s real async/gesture internals directly.
- `gradlew`/`gradle-wrapper.jar` — the Gradle wrapper, actually generated and committed (had never
  been before, despite `gradle-wrapper.properties` existing) so a future from-scratch attempt
  doesn't have to redo that regeneration step.

## Status

Built and iterated across two sessions (2026-09-06): first proved the Android/Kotlin/Gradle
toolchain works on this machine with a deliberately small first cut, then a working photo grid
(Coil for image loading/caching/EXIF rotation — fixing a genuine Kotlin elvis-operator bug that
left every thumbnail blank, see
[documentation/bugs/repo/fixed/2026-09-06-photo-grid-always-blank-bounds-decode-null-trips-elvis-always-returns-null-thumbnail-SOLVED.md](../../documentation/bugs/repo/fixed/2026-09-06-photo-grid-always-blank-bounds-decode-null-trips-elvis-always-returns-null-thumbnail-SOLVED.md)),
tap-to-fullscreen, swipe-between-photos, and pinch-to-zoom/pan — all confirmed working end to end
on the `Motorola_Moto_G54_5G` AVD with real test photos, all covered by Robolectric tests.
Unstarted at archive time: on-device quality scoring, on-device object detection (the reference
detector for that is [previous-work/pictures-pipeline/objects.py](../pictures-pipeline/objects.py)
— itself also just a reference, never ported), sync to a server, automatic background trigger —
none of that got past writing a next-session prompt before the pivot to React.

**Toolchain notes worth keeping**, useful again if a native Android app is ever revisited: Gradle
needs a JDK it can actually run under — this machine's Android-Studio-bundled JBR 25 crashes
Gradle 8.14.5's embedded Kotlin compiler (fails parsing the version string), a separate JBR 21
install (`~/.jdks/jbr-21.0.11`) works. Coil was deliberately pinned to 3.1.0 rather than the latest
3.6.2, since 3.2.0+ needs a newer `compileSdk`/Android Gradle Plugin than this project had pinned
(8.13.0 AGP, `compileSdk`/`targetSdk` 36) — check freshness again from scratch if resumed, don't
assume these pins still make sense. Android Studio and its SDK were installed self-contained into
Joakim's own home directory (`~/Android/Sdk`), no `apt`/snap package, per this repo's
no-system-wide-toolchain rule.
