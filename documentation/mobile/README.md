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

**Not yet verified to actually build or run.** Written before Android Studio/an SDK existed on this
machine; Joakim has since installed both (self-contained, per the toolchain note below) and is
working through first-sync errors as they surface — two fixed so far without ever running a build:
`kotlinOptions { jvmTarget = "17" }` is a hard error under Kotlin 2.4.0's Gradle plugin (migrated to
the `kotlin { compilerOptions { ... } }` DSL), and the Gradle wrapper was bumped from 8.13 to 8.14.5
(latest patch, includes two security fixes) after a deprecation warning. First real step once sync
succeeds: confirm the app actually installs and runs on a real device before changing anything else.

## Toolchain note

Per [POLICY.md](../policies/POLICY.md)'s no-system-wide-toolchain rule, Android Studio was installed
from the self-contained `.tar.gz` (developer.android.com/studio → Linux) into Joakim's own home
directory, and the SDK via Studio's own SDK Manager into `~/Android/Sdk` — no `apt`/snap package, no
sudo beyond the one-time 32-bit compatibility libraries the emulator itself needs on Ubuntu. Pinned
versions in `android/`: Android Gradle Plugin 8.13.0, Kotlin 2.4.0, Gradle 8.14.5, `compileSdk`/
`targetSdk` 36 — current stable as of 2026-09-06; check freshness again before the next real step,
per [WORKFLOW.md](../policies/WORKFLOW.md).

## Layout

- `android/app/src/main/java/com/dpfas/photobrowser/MainActivity.kt` — permission request, kicks
  off the `MediaStore` query on a background thread.
- `android/app/src/main/java/com/dpfas/photobrowser/PhotoAdapter.kt` — `GridView` adapter,
  decodes downsampled thumbnails off the main thread with a small in-memory cache.

See [TODO.md](TODO.md) for what's next.
