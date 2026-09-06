# Get the Android photo browser working end to end: Coil, tests, fullscreen tap

First real run of `android/app` (previously untested — see mobile/README.md). Fixed a genuine code
bug where the photo grid rendered solid blank cells for every photo, always (a Kotlin elvis-operator
gotcha around `BitmapFactory`'s bounds-only decode call, always returning early) — see the linked
bug report. Replaced the hand-rolled `BitmapFactory`/thread-pool/`LruCache` decode path with Coil
(memory+disk caching, automatic EXIF rotation), fixing a separate rotation bug as a side effect.
Added tap-to-fullscreen (`FullscreenPhotoActivity`) and Robolectric-based unit tests
(`PhotoAdapterTest`, `FullscreenPhotoActivityTest`) — the TDD exception this app started with is
now closed. Regenerated and committed the Gradle wrapper (`gradlew`/`gradle-wrapper.jar`), previously
gitignored despite `gradle-wrapper.properties` existing, so future sessions don't need to
regenerate it. Bumped Coil/Robolectric/androidx.test:core to current stable versions (Coil pinned
to 3.1.0 rather than latest 3.6.2 — newer versions need `compileSdk` 37, which needs a newer AGP
than this project currently pins; not chased this session).

Also chased down (not a code bug, Coil behaving as documented): Coil's in-memory cache requires an
*exact* size match by default, so viewing a photo fullscreen then scrolling back to its grid
thumbnail forced a disk-decode instead of an instant memory hit — fixed via `Precision.INEXACT`.
Separately, the memory cache gets evicted under real memory pressure (this dev machine runs Gradle
+ the emulator simultaneously) — accepted as expected, not fixed.

See [documentation/bugs/repo/fixed/2026-09-06-photo-grid-always-blank-bounds-decode-null-trips-elvis-always-returns-null-thumbnail-SOLVED.md](../bugs/repo/fixed/2026-09-06-photo-grid-always-blank-bounds-decode-null-trips-elvis-always-returns-null-thumbnail-SOLVED.md)
for the full bug writeup, and [mobile/README.md](../mobile/README.md)/[mobile/TODO.md](../mobile/TODO.md)
for current status and what's next (swipe-between-photos + pinch-zoom in fullscreen mode).

- **Doc size**: `mobile/README.md` +2167; `mobile/TODO.md` +876; `GLOSSARY.md` +4766;
  `tooling/README.md` +130; `tooling/TODO.md` +760. Net +8699 chars.
