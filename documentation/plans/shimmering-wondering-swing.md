# Native Android app — Slice 1 (photo listing skeleton)

## Context

This session started as "make the pictures web viewer (`modules/web/`, built earlier this session)
usable from a phone as a PWA." Working through the details surfaced a hard requirement that a PWA
cannot meet: Joakim wants "handling" (quality/object detection) to run on every photo *before* any
server round-trip, and wants a selective sync (not all pictures, not automatic-for-everything) to
happen **automatically in the background**, without opening an app. No browser API lets a web page
watch the OS photo library and act on new photos while closed — that boundary is real, confirmed
against this repo's own prior research (`documentation/curation/ARCHITECTURE.md`'s PWA-vs-native
capability check). So a native app is required for that one specific capability.

This reverses a standing, twice-reaffirmed 2026-09-05 decision
(`documentation/curation/IDENTITY_MATCHING.md`'s "Native app avoided as long as possible" section,
`documentation/security/THREATS.md` row 17) to avoid native apps — reasoned around app-store control
risk (Google Play/Apple can modify/re-sign a published binary, undermining the self-hosted control
model). Discussed directly with Joakim this session: automatic background photo-library watching is
exactly the "no PWA-reachable path" exception that decision itself carved out, not a casual override.
**Distribution stays sideloaded (a plain APK, no Google Play), which keeps the original concern
resolved** — the binary is never republished through a platform that could alter it.

Confirmed with Joakim this session:
- Android only for now; iOS is a standing "consider it, don't build it" note for every future step.
- Most pictures should be *handled* (differentiated: quality + object detection) locally, not
  copied to a server — only a user-selected subset syncs, and the user controls which pictures sync
  and how (not an automatic blanket backup).
- What was built earlier this session (`modules/web/`, the folder-scan viewer) is explicitly a
  mockup, to be archived **next session**, after this native app exists — not touched this pass.
- The old Postgres/FastAPI/Redis/Caddy stack (`archive/app`, `archive/server`, `archive/detector`)
  is fully disregarded per `archive/README.md`'s own instruction ("ask before carrying a decision
  forward, don't assume it still applies") — **not revived**. The sync backend this app eventually
  talks to extends `modules/pictures.py`'s live SQLite register instead, since that's this restart's
  actual live foundation (confirmed via `git ls-tree master` — `master` only has `modules/quality.py`,
  none of `pictures.py`/`objects.py`/`web/`, all of which live only on `test_production1`).
- New branch off `master` (not `test_production1`) — this is unrelated, different-toolchain work.
  Note: because `master` lacks `modules/pictures.py` entirely, the *sync* slice (below, not built
  this pass) will need `test_production1` merged into `master` first, or a rebase at that point —
  not a blocker for this pass, since Slice 1 doesn't touch syncing at all.
- No JDK/Android SDK/Gradle exists on this dev machine; Docker does.

## Roadmap (this pass is Slice 1 only)

1. **Slice 1 (this pass)**: Android app skeleton — permission handling, MediaStore photo
   enumeration, a simple photo grid. No detection, no sync yet.
2. Slice 2 (later): port `modules/quality.py`'s blur/exposure/saturation to Kotlin, computed
   on-device per photo, parity-tested against the Python implementation's output on fixed images.
3. Slice 3 (later): port `modules/objects.py`'s NanoDet-Plus detection via ONNX Runtime Mobile —
   flagged by research as the highest-effort piece (the distribution-focal-loss decode math is a
   from-scratch numerical reimplementation, not a library call; needs its own parity tests against
   Python's known output, not just visual sanity-checking).
4. Slice 4 (later): user-driven sync — multi-select which photos sync, upload original bytes +
   on-device-computed findings to a new server endpoint extending `modules/pictures.py`'s register
   with findings persistence (a schema decision not made yet).
5. Slice 5 (later): automatic/background trigger (`WorkManager` periodic job) plus real "how" sync
   controls (Wi-Fi-only, etc.) — the actual capability that made native necessary in the first place.

## Slice 1 concrete plan

**New top-level `android/` folder** (git-tracked), Kotlin + Gradle Kotlin DSL, Jetpack Compose UI,
`minSdk 26` / latest stable `compileSdk`/`targetSdk`. Per this repo's doc-layout convention (code
dirs get a one-line stub, real content lives under `documentation/`):
- `android/README.md` — one-line stub pointing to `documentation/mobile/README.md`.
- `documentation/mobile/README.md` + `documentation/mobile/TODO.md` — the roadmap above, added to
  `documentation/README.md`'s top-level folder-index table.
- `documentation/curation/IDENTITY_MATCHING.md`'s "Native app avoided as long as possible" section
  gets a dated addendum recording this reversal and its reasoning — appended, not rewritten.
- `documentation/GLOSSARY.md`: append terms as they're actually used while writing code this pass
  (e.g. `MediaStore`, `Robolectric`, `ContentResolver`) — same-turn rule applies during
  implementation, not deferred to a summary.

**Code, TDD throughout (write the failing test first, same as every other pass this session):**
- `android/app/src/main/java/.../PhotoRepository.kt` — wraps
  `ContentResolver.query(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, ...)`, returns a list of
  photo records (uri, display name, size, date-taken). Tested via Robolectric's shadow content
  resolver with fake inserted rows — no emulator/device needed, matches this repo's existing
  "fast, in-process tests" preference (`modules/tests`, `contacts/tests`).
- A single Compose screen: permission request (`READ_MEDIA_IMAGES` for API 33+, `READ_EXTERNAL_
  STORAGE` with `maxSdkVersion="32"` for older) → once granted, a grid of photo thumbnails.
- Explicitly out of scope this pass: quality/object detection, sync/upload, background triggers —
  tracked as Slices 2-5 in `documentation/mobile/TODO.md`, not built now.

**Verification**: no JDK/Android SDK exists on this machine, so I'll attempt a Docker-based headless
build+test (`docker run` against an Android-SDK-capable image, `./gradlew testDebugUnitTest` for the
Robolectric tests) to actually confirm the code compiles and tests pass, rather than just asserting
correctness by inspection. Real risk this hits friction (SDK license acceptance, image size/network) —
if so, I'll hand Joakim exact commands to run locally instead (needs Android Studio installed there,
a system-level install POLICY.md says I must never run myself). Will ask before running `docker run`
per this session's docker-hygiene convention, and before creating the branch, at implementation time.

## Explicitly deferred, not decided in this plan

- Exact "which pictures sync, and how" UI/rules (Slice 4/5).
- Whether findings persist server-side as new `databases/app.db` columns/tables, or another shape
  (small schema decision, made when Slice 4 is actually planned).
- iOS — acknowledged per Joakim's standing note, not scoped or estimated here.
- Archiving `modules/web/` — next session, per Joakim's own instruction, not this pass.
