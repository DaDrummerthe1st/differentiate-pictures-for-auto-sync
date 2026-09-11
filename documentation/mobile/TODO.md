# mobile/ TODO

- **Confirmed working, 2026-09-11** (`android-app-test1`, 83/83 unit tests): "Show detected faces"
  is now a persistent icon toggle rather than a session-only `CheckBox` — Joakim asked for this
  pattern (filled/outline icon reflecting on/off state, and the choice surviving both swiping
  between photos and a full app restart) to apply to **every** toggleable setting built from now
  on, not just this one. Added `android/app/src/main/java/com/dpfas/photobrowser/settings/AppSettings.kt`,
  a small `SharedPreferences`-backed class - new persistent settings should be added there as
  another property rather than reading/writing preferences ad hoc elsewhere. `FullscreenPhotoActivity`
  reads the persisted value on `onCreate` and writes it back on every toggle tap; the icon itself
  is a rounded-rectangle `<shape>` drawable (`ic_detect_boxes_on`/`_off`, filled vs. outlined) rather
  than a `CheckBox`, echoing the setting's own subject (a bounding box).
- **Confirmed working, 2026-09-09** (`android-app-test1`, build green, 78/78 tests, verified on
  `Motorola_Moto_G54_5G` emulator): on-device face detection + embedding pipeline
  (`android/app/src/main/java/com/dpfas/photobrowser/facerecognition/` —
  `YuNetFaceDetector`/`MobileFaceNetEmbedder` via ONNX Runtime Mobile, decode math ported from
  OpenCV's `face_detect.cpp`, preprocessing verified against InsightFace's own `inference.py`,
  vendored models + license notes in `android/app/src/main/assets/models/LICENSES.md`), an
  off-by-default "Show detected faces" box overlay in the fullscreen viewer only (grid stays
  untouched, per the existing badge-not-boxes decision), and tap-a-face similar-faces search
  (`SimilarFacesActivity`, cosine similarity over the 512-d embeddings, ranked via
  `FaceSimilarity.findSimilar`). Runs automatically over the visible gallery on launch, logs to
  Logcat (`FaceScan` tag), shows a summary Toast. See [../GLOSSARY.md](../GLOSSARY.md) for ONNX
  Runtime / YuNet terms already defined there.
  - **Known simplification, not yet built**: face crops for embedding use a plain axis-aligned
    box-plus-margin crop, not the landmark-based ArcFace 5-point similarity-transform alignment
    MobileFaceNet-family models are trained on. Leading (unconfirmed) suspect for
    `documentation/bugs/repo/under_process/2026-09-09-similar-faces-search-returns-increasingly-wrong-matches-past-the-first-result.md` —
    real embedding-score data needed before deciding whether to build it; see that bug file's
    "next session should start with" section.
  - Two throwaway swipe-triage grid demos also added this session (`triage/` package, reachable
    via the main grid's overflow menu) — fake Toast/log persistence only, matching the Option
    A/B comparison spec in [UX_FLOWS.md](UX_FLOWS.md); not polished, not a real build.
  - No entity/naming UI yet — similar-faces is "find more like this," not "who is this."
- **Backlog snapshot, 2026-09-09** (design/discussion session, `android-app-test1`, no code touched):
  consolidated the open backlog into one checklist for session planning — not new information, just
  a pointer list. Written here as plain markdown rather than a TodoWrite-tracked list because
  TodoWrite is currently unavailable in this session — tracked as a claude-bug in the separate
  `claudefiles` repo (`documentation/bugs/claude-bugs/under_process/2026-09-07-todowrite-tool-silently-disappeared-after-extension-autoupdate.md`,
  not linked directly since it's a different git repository); confirmed 2026-09-09 that the applied
  mitigation is active but did not restore the tool, likely a hard upstream gate.
  - [ ] Swipe-to-triage build slice — design confirmed (right=keep/left=remove, manual-purge
    default); next step is a concrete build plan (gesture detection, Removed-bin schema on the Room
    table, undo snackbar) — see [UX_FLOWS.md](UX_FLOWS.md).
  - [ ] Bounding-box grid badge — corner-badge treatment proposed, icon/placement undecided;
    blocked on on-device object detection existing.
  - [ ] Sort/order control — user-chosen ordering, not designed at all yet.
  - [ ] Folder-usage-frequency signal — logged as a hint only, no concrete use or UX direction.
  - [ ] Storage-transparency dashboard — device/NAS/cloud/paid breakdown, not designed.
  - [ ] On-device object detection — design fresh for Kotlin/Android, NanoDet-Plus/MNN as
    inspiration only.
  - [ ] Logistic regression for usage-intent — newly raised in
    [../curation/TODO.md](../curation/TODO.md), not yet evaluated against the existing hand-weighted
    scoring design in [../curation/IDENTITY_MATCHING.md](../curation/IDENTITY_MATCHING.md).
  - [ ] Ambiguous/tied scoring — open question: what happens when two competing signals tie.
  - [ ] *(deferred, own session/worktree)* NAS/backup-sync structure.
  - [ ] *(standing, not a task)* iOS — "consider it, don't build it."
- **NAS sync-contract review — started, not finished, 2026-09-09** (`android-app-test1`, no code
  touched this pass): the nas-design session's `documentation/nas/SYNC_CONTRACT.md` (exists only
  on `worktree-nas-server-design`, not merged here — read read-only from this branch via
  `git show worktree-nas-server-design:documentation/nas/SYNC_CONTRACT.md`) asks in its own
  Status section for this topic to review it before either side builds against it. Session was
  paused before finishing — pick back up by reading that file fresh (or messaging the nas-design
  session directly if still live, see below) rather than re-deriving the below from memory:
  - Wrongly framed the review as blocked on client direction (native Kotlin vs. the 2026-09-06
    React-client pivot) by diffing `SYNC_CONTRACT.md`'s native-Android assumptions (background
    sync worker, Android Keystore device-key storage) against **master's** stale copy of
    [../VISION.md](../VISION.md). That was this session's own mistake, caught before acting on
    it: *this branch's* VISION.md already resolved client direction 2026-09-07 ("Decision: stay
    on native Kotlin/`android-app-test1`", its iOS-parity note) — master just hasn't merged that
    reversal yet, ordinary branch divergence, not an open question. Reconcile master's
    "React-client pivot" section with this branch's later decision when this branch merges;
    don't overwrite one with the other blind.
  - [ ] **Real remaining work, not started**: check `SYNC_CONTRACT.md`'s native-Android
    assumptions against this branch's actual Kotlin code. The nas-design session's own 2026-09-09
    self-review already fixed two internal contradictions before handoff — don't re-flag these as
    new: (1) selective backup vs. an earlier line claiming every original eventually lands on the
    NAS regardless of user choice, corrected to fully selective/user-chosen; (2) device revocation
    hard-deleting the `devices` row vs. DATA_MODEL.md's soft `revoked_at`, resolved in favor of
    soft-revoke. Also renamed the `explicit-backup` sync-queue reason to `preset-full-backup` to
    match. Two sub-questions the nas-design session explicitly left open for this review: no
    expiry/single-use/rate-limit specified on the one-time pairing code (`POST /pairing/claim`),
    and no path to cancel a queued `/sync/queue` request if the phone deletes a photo locally
    before uploading its original.
  - [ ] If the nas-design session is still live when this resumes, message it directly
    (`ListAgents`) instead of re-deriving the contract from the doc alone — cross-session
    `SendMessage` is available now, no longer strictly a hand-it-to-Joakim-by-hand process.
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
- **Resume the deferred roadmap once swipe/zoom is settled**: on-device quality scoring and
  on-device object detection, designed fresh for Kotlin/Android and taking
  `previous-work/pictures-pipeline/quality.py`/`objects.py` only as design inspiration (the
  scoring approach, the model choice) — not code to port, adapt, or otherwise build on top of.
  User-driven sync to a server, automatic background trigger: also none of this scoped yet.
  `previous-work/` is archived, disregarded-as-code reference only, per
  [../../previous-work/README.md](../../previous-work/README.md).
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
  the credit/confidence-display mechanic. Bringing any of this on-device is a fresh Kotlin/Android
  build guided by that design (Room instead of Postgres, on-device ONNX Runtime/MNN instead of a
  server-side Python process) — `curation/`'s server-side notes and `previous-work/`'s Python code
  are both design inspiration, not something to port or copy from. When the on-device build
  happens, flag any place it deviates from a `curation/` doc's server-side assumption inline in
  that doc, same convention already used elsewhere (e.g. `curation/IDENTITY_MATCHING.md`'s
  "Reversed 2026-09-05" note), rather than silently diverging.
- **On-device runtime pick — researched 2026-09-07, not yet decided**: `com.microsoft.onnxruntime:onnxruntime-android` (Maven Central, MIT, currently 1.27.0) is the direct on-device counterpart to the server-side picks (same `.onnx` files, NNAPI/XNNPACK hardware acceleration on Android). Two real mobile-purpose-built alternatives exist that also consume ONNX models (via import/conversion, not direct execution): **ncnn** (Tencent, BSD-3-Clause, lighter footprint, NanoDet-Plus's own official repo ships an ncnn deployment path specifically) and **MNN** (Alibaba, Apache-2.0). Correction to an initial framing: neither is meaningfully "more open source" than ONNX Runtime — all three are single-company-led OSS with similarly permissive licenses; the real trade-off is mobile-optimized footprint/speed vs. ONNX Runtime's broader format compatibility and reuse of the exact same server-side model files with zero conversion step. **Decided 2026-09-07: MNN** over ncnn — both fit fine on pure permissiveness, but MNN's Apache-2.0 matches the license family already used everywhere else in this project (NanoDet-Plus, RapidOCR) rather than adding a third distinct license (ncnn's BSD-3-Clause) with no demonstrated technical reason yet, and Apache-2.0's explicit patent grant is a real extra protection BSD-3-Clause lacks. All three runtimes' research notes kept for reference, not discarded. Still worth a real footprint/speed comparison once object-detection porting actually starts.
  - **Unresolved conflict, surfaced 2026-09-09**: an entirely separate worktree branch, `worktree-android-native-ai-stack` (commit `8dfac99`, 2026-09-06, one day *before* the MNN decision above), independently picked **OpenCV** as the on-device runtime (one codebase across Android/iOS/Linux, DBSCAN face clustering designed against it) — with no cross-reference either direction. Neither branch's session knew about the other's pick; no doc or bug file recorded a resolution (confirmed 2026-09-09 by a peer session searching this repo's own history). Separately, this session found the MNN Maven AAR has **no usable Java API on this x86_64 emulator** — its artifact only ships arm64/armv7 native `.so` files, no x86_64 build — so it can't even be evaluated here as-is. The face-recognition pipeline built this session (`android/app/src/main/java/com/dpfas/photobrowser/facerecognition/`) therefore used a **third** runtime, `onnxruntime-android` 1.29.0, purely as the pragmatic unblocking choice, not a resolution of the conflict. **Joakim's call, 2026-09-09: defer** — don't standardize now, keep ONNX Runtime Mobile under the working code as-is, revisit runtime strategy (OpenCV vs. MNN vs. ONNX Runtime Mobile, and whether "one runtime" is even the right frame vs. per-model picks) in a dedicated session. Whoever picks this up next should treat this as still fully open, not settled by precedent of "most code currently uses ONNX."
- **Open design question, raised 2026-09-07, not addressed anywhere in `curation/` yet**: can the
  on-device suggestion/scoring logic get stuck when a photo scores equally under two competing
  signals (e.g. "keep" and "delete" candidates tie)? Logged as new, unresolved — see
  [../curation/TODO.md](../curation/TODO.md)'s matching entry.
- **Backlog raised 2026-09-07, none designed or scoped yet** (deliberately logged, not built: a
  second AI session was concurrently active on this same branch/checkout at the time, with no
  worktree isolation between them, so building blind risked a real file collision — and the list
  itself was too large for one session regardless):
  - **Swipe-to-triage gesture** — design discussion started 2026-09-07, see
    [UX_FLOWS.md](UX_FLOWS.md): a two-way swipe (remove-from-view vs. organize/tag), a two-tier
    recoverability model (immediate undo + a durable, never-auto-purged-by-default "Removed" bin)
    satisfying Joakim's hard always-recoverable rule. Awaiting his confirmation on the left/right
    direction mapping before this is build-ready.
  - **Bounding boxes surfaced in the grid view itself**, not just the fullscreen view, once
    object detection is on-device — needs a concrete visual treatment, not just "draw a box."
  - **Sort/order control**, user-chosen, always available — not a fixed default ordering.
  - **Folder-usage-frequency signal** — track which folders/albums get used more, no concrete use
    identified yet, logged as a hint for future visualization decisions.
  - **Storage-transparency dashboard**: total storage used across device/NAS/cloud/paid tiers,
    shown plainly so the user stays in control of what to delete and where — explicitly positioned
    against services that obscure this to keep usage growing. Central to why deletion-focused
    curation works at all (seeing the real number is what makes "delete more" feel possible).
  - **Confidence-score-driven NAS request flow** (depends on the NAS/backup-sync work below): once
    a NAS exists, it computes a confidence score per photo and requests upload of specifically the
    photos it's least confident about, rather than the phone pushing everything. A file present on
    both phone and NAS independently needs to be flagged/reconciled, not treated as two unrelated
    copies.
  - **NAS/backup-sync structure — recommended as its own session, own branch, own worktree**: a
    genuinely separate subsystem (targets `192.168.1.10` directly, no expensive SSD/RPi storage
    needed) with no file overlap with `android/`, so it's also the cleanest fix for this session's
    concurrent-editing concern — a different worktree means a different directory, not just a
    different branch checked out in the same one.
- iOS: still a "consider it, don't build it" note, unchanged.
- **Dev conventions, standing**: development/testing defaults to the emulator (`Motorola_Moto_G54_5G` AVD) only — never install/launch on Joakim's physical phone unless he explicitly asks, even if it was previously sideloaded for a demo. Debug GUI behavior via logcat/instrumentation (`Log.d`, `dumpsys`, `uiautomator dump`), not screenshots — see `WORKFLOW.md`'s Debugging discipline section, applies here too.
