# mobile/

The native Android app (`android/` at repo root) — sideloaded only, no Google Play. Full
background/reasoning for why a native app exists at all: [../VISION.md](../VISION.md)'s
"Native-app pivot" section.

## Status — 2026-09-06

First cut, built this session: `android/app` is a single-Activity Kotlin app that requests photo
access and shows a grid of the device's photos via `MediaStore` — nothing else. Joakim asked for
this deliberately small, to prove the Android/Kotlin/Gradle toolchain actually works on this
machine before investing in anything bigger. A fuller multi-slice plan (Jetpack Compose,
Robolectric-based TDD, on-device quality/object detection, sync) was drafted the session before
this one and then explicitly scrapped, unbuilt, at Joakim's request — treat this app as a
from-scratch first cut, not a continuation of that plan.

**Deliberate exception to this repo's TDD rule**: no tests were written for this pass, by Joakim's
explicit direction — this is a disposable toolchain check, not a foundation to build on carefully.
Flagging it here rather than silently skipping the rule; the next real slice of Android work
should return to normal TDD practice.

**Not yet verified to actually build or run** — written without Android Studio/an Android SDK on
this machine (none installed at the time of writing); Joakim is installing Android Studio in
parallel. First real step for the next session touching this: open `android/` in Android Studio,
let it sync/generate the Gradle wrapper, and confirm the app installs and runs on a real device
before changing anything.

## Toolchain note

Per [POLICY.md](../policies/POLICY.md)'s no-system-wide-toolchain rule, install Android Studio from
the self-contained `.tar.gz` (developer.android.com/studio → Linux), extracted into a project-local
or otherwise non-system directory — not via `apt`/snap. The Android Gradle Plugin (8.13.0) and
Kotlin (2.4.0) versions pinned in `android/build.gradle.kts` were the current stable releases as of
2026-09-06 — check freshness again before the next real step, per [WORKFLOW.md](../policies/WORKFLOW.md).

## Layout

- `android/app/src/main/java/com/dpfas/photobrowser/MainActivity.kt` — permission request, kicks
  off the `MediaStore` query on a background thread.
- `android/app/src/main/java/com/dpfas/photobrowser/PhotoAdapter.kt` — `GridView` adapter,
  decodes downsampled thumbnails off the main thread with a small in-memory cache.

See [TODO.md](TODO.md) for what's next.
