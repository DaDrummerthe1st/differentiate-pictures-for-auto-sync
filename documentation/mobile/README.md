# mobile/

**Superseded 2026-09-06 by the React-client pivot** — see [../VISION.md](../VISION.md)'s
2026-09-06 note. The native Kotlin/Android app this file describes is archived, code-disregarded
reference at [../../previous-work/kotlin/](../../previous-work/kotlin/README.md); nothing below
describes a currently-planned build. The UI/UX goals it reached (photo grid, tap-to-fullscreen,
swipe, pinch-to-zoom) are still the target — the next session starts the client over from scratch
in React, not resuming this implementation.

The native Android app (archived at `previous-work/kotlin/`, was `android/` at repo root) —
sideloaded only, no Google Play. Full background/reasoning for why a native app existed at all:
[../VISION.md](../VISION.md)'s "Native-app pivot" section.

## Status — 2026-09-06

Built this session as a deliberately small first cut to prove the Android/Kotlin/Gradle toolchain
works on this machine, then confirmed working end-to-end and extended: `android/app` is a
single-Activity Kotlin app that requests photo access, shows a grid of the device's photos via
`MediaStore`, and supports tapping a photo to view it fullscreen. Image loading, memory/disk
caching, and EXIF rotation are handled by [Coil](https://coil-kt.github.io/coil/) rather than
hand-rolled `BitmapFactory` code — see the Layout section below and the fixed bug report linked
there for why. The originally-planned Robolectric-based TDD (part of a fuller multi-slice plan
drafted the session before this one, then explicitly scrapped) is now in place after all —
`android/app/src/test/` covers `PhotoAdapter`/`FullscreenPhotoActivity`'s own wiring logic via an
injectable-seam pattern rather than exercising Coil's real async engine in tests.

**Toolchain notes**:
- The Gradle wrapper (`gradlew`/`gradle-wrapper.jar`) is now committed — it had never actually
  been generated before this session despite `gradle-wrapper.properties` existing, and was
  previously gitignored (regenerated via a one-off Gradle 8.14.5 install pointed at the project).
- Gradle 8.14.5 needs a JDK it can actually run under: this machine's Android-Studio-bundled JBR 25
  crashes Gradle's embedded Kotlin compiler (fails parsing the version string) — build with
  `JAVA_HOME=~/.jdks/jbr-21.0.11` (a separate, already-present JBR 21) instead.
- A `.vscode/tasks.json` task ("Android: Run app (install + launch)", bound to VS Code's default
  build task / Ctrl+Shift+B) wraps `./gradlew installDebug` + `adb shell am start` for running from
  VS Codium.

**Bugs hit and fixed this session**: the photo grid initially rendered as solid blank cells for
every photo, always — a Kotlin elvis-operator (`?:`) gotcha in the original hand-rolled decode
code; root-caused and fixed, see
[documentation/bugs/repo/fixed/2026-09-06-photo-grid-always-blank-bounds-decode-null-trips-elvis-always-returns-null-thumbnail-SOLVED.md](../bugs/repo/fixed/2026-09-06-photo-grid-always-blank-bounds-decode-null-trips-elvis-always-returns-null-thumbnail-SOLVED.md).
Separately, Coil's default memory-cache key requires an *exact* size match to reuse a cached
bitmap — fixed by requesting thumbnails at a fixed size with `Precision.INEXACT` so a
larger-cached version (e.g. from viewing the same photo fullscreen) still counts as a hit; see
`PhotoAdapter.kt`'s comments.

Verified end-to-end on the `Motorola_Moto_G54_5G` AVD with real (private, gitignored — never
committed, see `resources/test_pictures/`) test photos: the grid shows and scrolls through all of
them correctly, EXIF-rotated photos display right-side-up, and tap-to-fullscreen works.

**Swipe/zoom added, same session**: `FullscreenPhotoActivity` now shows a swipeable `ViewPager2`
across the whole photo list (not just the tapped photo), each page an `io.getstream.photoview`
`PhotoView` for pinch-to-zoom/pan — see [TODO.md](TODO.md) for the library evaluation. Both swipe
and pinch-to-zoom confirmed working by Joakim on the emulator.

**Known, accepted non-issue**: Coil's in-memory cache gets evicted under real memory pressure
(this dev machine runs Gradle + the emulator simultaneously — unusually heavy; a real phone would
see this far less), falling back to its disk cache (fast, not instant) rather than a full re-decode.
Joakim explicitly accepted this as fine.

## Toolchain note

Per [POLICY.md](../policies/POLICY.md)'s no-system-wide-toolchain rule, Android Studio was installed
from the self-contained `.tar.gz` (developer.android.com/studio → Linux) into Joakim's own home
directory, and the SDK via Studio's own SDK Manager into `~/Android/Sdk` — no `apt`/snap package, no
sudo beyond the one-time 32-bit compatibility libraries the emulator itself needs on Ubuntu. Pinned
versions in `android/`: Android Gradle Plugin 8.13.0, Kotlin 2.4.0, Gradle 8.14.5, `compileSdk`/
`targetSdk` 36 — current stable as of 2026-09-06. Coil is deliberately pinned to 3.1.0 rather than
the latest 3.6.2: 3.2.0+ requires `compileSdk` 37, which needs a newer Android Gradle Plugin than
8.13.0 supports — bumping that whole chain wasn't warranted for a routine freshness check. Check
freshness again before the next real step, per [WORKFLOW.md](../policies/WORKFLOW.md).

## Layout

- `android/app/src/main/java/com/dpfas/photobrowser/MainActivity.kt` — permission request, kicks
  off the `MediaStore` query on a background thread, wires tap-to-fullscreen.
- `android/app/src/main/java/com/dpfas/photobrowser/PhotoAdapter.kt` — `GridView` adapter; delegates
  actual image loading/caching to Coil via an injectable `loadImage` lambda (real implementation in
  production, a recording fake in `PhotoAdapterTest.kt`).
- `android/app/src/main/java/com/dpfas/photobrowser/FullscreenPhotoActivity.kt` — fullscreen,
  swipeable (`ViewPager2`) view across the whole photo list, opened at the tapped position.
- `android/app/src/main/java/com/dpfas/photobrowser/FullscreenPhotoPagerAdapter.kt` — the
  `ViewPager2`'s adapter; delegates loading into each page's `PhotoView` to the same kind of
  injectable `loadImage` lambda pattern as `PhotoAdapter`.
- `android/app/src/main/java/com/dpfas/photobrowser/PhotoBrowserApplication.kt` — configures Coil's
  singleton `ImageLoader` (debug-only logging via `BuildConfig.DEBUG`).

See [TODO.md](TODO.md) for what's next.
