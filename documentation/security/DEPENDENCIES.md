# Dependency audit

A full-repo inventory of every external dependency, done after the native-app pivot
([../VISION.md](../VISION.md)). Documentation-only — no dependency was upgraded, removed, or
replaced as part of this pass. Three parallel research passes (Android/Gradle, Python/Docker,
vendored AI model picks) checked license, maintenance health, and CVE status against live sources
(GitHub/OSV.dev/PyPI/vendor sites), not training-data memory or a package manager's self-reported
tag.

**Convention used throughout**: every table below separates **last activity date** from
**activity pattern** — a raw "last pushed" date can't tell "healthy and actively developed" apart
from "CI/tooling commits keep landing but no real feature has shipped in years"
(`io.getstream:photoview`), "actively steering users elsewhere without formally archiving"
(Open Model Zoo), or "declared end-of-life by its own maintainers, not neglect" (JUnit4) — and the
inverse matters too: a repo with a high PR/commit volume that rarely merges anything is a worse
health signal than one with low but steady, actually-landing activity. Raised by Joakim 2026-09-06
as a gap in this audit's first draft.

**Correction to this audit's own starting premise, now resolved**:
[POLICY.md](../policies/POLICY.md)'s "## Licensing" section originally didn't state a project-wide
MIT/Apache-2.0-only bar — it only said no open-source license had been chosen *for this project
itself* yet. The MIT/Apache-2.0-only bar referenced repeatedly below had, until this pass, only
been written down in [curation/DETECTORS.md](../curation/DETECTORS.md), scoped there to vendored AI
model code/weights. **Joakim resolved this 2026-09-06: the bar applies to every dependency this
project takes on**, not just AI models — now recorded in POLICY.md itself. That makes three
findings below **confirmed policy violations, not just factual notes**: `junit:junit:4.13.2`
(EPL-1.0, test-only), `psycopg[binary]` (LGPL-3.0), and `mysql-connector-python` (GPL-2.0 +
Oracle's FOSS exception) — each needs a remediation plan, see "Open items" below.

## Android / Gradle (`android/`)

The one actually-shipping ecosystem — everything else below is either superseded
(`previous-work/`) or not yet integrated (AI model picks).

Split deliberately into **last activity date** and **activity pattern** — a recent commit alone
doesn't distinguish "healthy, actively developed" from "the CI config gets bumped but no real code
has shipped in years," and a repo with three PRs a week that never merge is worse than one with no
open PRs at all. Raised by Joakim 2026-09-06 as the datapoint this table was missing.

| Dependency | License | Last activity | Activity pattern | CVE |
| --- | --- | --- | --- | --- |
| `com.android.application` (AGP) 8.13.0 | Apache-2.0 | 8.13.0 released 2025-09-02; newer AGP releases have shipped since | Google-backed, regular release-train cadence — pin is ~1 year old but upstream isn't stagnant | None found (OSV) |
| `org.jetbrains.kotlin.android` 2.4.0 | Apache-2.0 | 2.4.0 released 2026-06-03 | JetBrains-backed, steady major/minor cadence | None found |
| `androidx.core:core-ktx:1.15.0` | Apache-2.0 | Current AndroidX core is up to 1.19.0 (several releases since 1.15.0) | Google/AndroidX continuous release train | None (OSV) |
| `androidx.appcompat:appcompat:1.7.0` | Apache-2.0 | Part of the same AndroidX release train | Google/AndroidX, org-backed | None (OSV) |
| `com.google.android.material:material:1.12.0` | Apache-2.0 (confirmed via GitHub API) | Repo pushed 2026-06-22 | Google-backed, regular releases | None (OSV) |
| `io.coil-kt.coil3:coil:3.1.0` | Apache-2.0 (confirmed) | 3.6.2 released 2026-09-04, days before this audit | Extremely active upstream — several minors ahead of the pin, which is deliberate ([mobile/README.md](../mobile/README.md): 3.2.0+ needs `compileSdk` 37), not stagnation | None (OSV) |
| `io.getstream:photoview:1.0.3` | Apache-2.0 (verified via GitHub API) | Repo pushed as recently as 2026-09-01 | **The pattern to watch for**: pushes keep landing (CI/workflow housekeeping only), but no functional library release has shipped since 1.0.3 on 2025-02-13 — 19+ months. Looks alive by "last push" date alone; isn't, by "last real feature" date. See "PhotoView lineage" below | None (OSV) |
| `junit:junit:4.13.2` (test) | **EPL-1.0 — CONFIRMED VIOLATION** | N/A — junit-team declared JUnit4 **formal maintenance mode** | Deliberate, declared end-of-life-as-a-feature-line by its own maintainers (critical/security fixes only, new work goes to JUnit5) — a stated end-state, not neglect or a stalled PR queue | None (CVE-2020-15250 already fixed in 4.13.1) |
| `org.robolectric:robolectric:4.16.1` (test) | MIT (raw LICENSE file confirmed; GitHub's own detector mis-reports "NOASSERTION") | 4.17-beta already shipping | Fast-moving, community+org backed (Google, LinkedIn, Robolectric Foundation) | None (OSV) |
| `androidx.test:core:1.7.0` (test) | Apache-2.0 | Repo pushed 2026-09-04 | Google/AndroidX, org-backed | None (OSV) |

**`junit:junit:4.13.2` is a confirmed MIT/Apache-2.0-bar violation** (resolved 2026-09-06 — see
"Open items" below for the remediation plan; note JUnit5/Jupiter is EPL-2.0, so it isn't a
compliant swap either).

### PhotoView lineage — doc correction made this pass

`android/app/build.gradle.kts` pins `io.getstream:photoview:1.0.3` — this is **already** the
replacement for the archived original, not a still-open risk. A parallel session's finding
("PhotoView is archived since October 2022, needs a replacement recommendation") describes
`chrisbanes/PhotoView`, the *rejected* original, and one factual detail in it doesn't hold up:

- `chrisbanes/PhotoView` was **not** GitHub-archived. It was **transferred/renamed to
  `Baseflow/PhotoView`** (still a live, non-archived repo), last commit 2022-03-25. The "archived
  since October 2022" date belongs to a different, unrelated fork
  (`UweTrottmann/PhotoView`, genuinely archived 2022-10-20) that this project's docs had conflated
  with the real one.
- The actually-adopted `io.getstream:photoview` fork (Stream's own fork, `GetStream/photoview-android`
  on GitHub, published to Maven Central) is real, Apache-2.0, and not abandoned — but it's
  **maintained, not actively developed**: release history is 1.0.0 (2024-02-15) → 1.0.1
  (2024-02-21) → 1.0.2 (2024-06-19) → 1.0.3 (2025-02-13), then nothing but CI/tooling commits for
  19+ months. `documentation/mobile/TODO.md` and `documentation/GLOSSARY.md` both called this
  "actively maintained," corrected this pass to "maintained but dormant on library code."
- No better MIT/Apache-2.0 alternative was found. `com.jsibbold:zoomage` (the only other
  Maven-Central option this project already considered) has had no commits since 2021 — worse,
  not better. **Recommendation: keep the current pick, just track it** — it's the least-stale
  realistic option, not a candidate for near-term replacement.

## Python (`previous-work/`) — superseded, not currently deployed

Per [documentation/README.md](../README.md), `previous-work/` holds disregarded implementations
kept for reference after the native-app pivot — this is a health inventory for a codebase that
isn't running anywhere today, not a live production posture. Still, every CVE-bearing package
below is already pinned to its fix version.

Same last-activity-vs-activity-pattern split as the Android table above.

| Package (pinned) | License | Last activity | Activity pattern | CVE status |
| --- | --- | --- | --- | --- |
| `vobject==0.9.9` (contacts-import) | Apache-2.0 | No PyPI release in 12+ months | **Genuinely stalled** — legacy Py2-compat branch, not a "quiet because stable" case | None found |
| `fastapi==0.141.1` | MIT | Released 2026-07-29 | Active, regular release cadence | None open |
| `uvicorn[standard]==0.52.1` | BSD-3-Clause | 0.52.4 now released | Active; routine patch cadence | None; minor bump available, not urgent |
| `pillow==12.3.0` | HPND | Released 2026-07-01 | Active, regular security-response cadence | **Is the fix version** for CVE-2026-55379 / CVE-2026-54060 |
| `python-multipart==0.0.32` | Apache-2.0 | PyPI-latest | Active | **Is the fix version** for CVE-2026-40347 / CVE-2026-53537 / CVE-2026-24486 |
| `pyjwt==2.13.0` | MIT | Current | Active, regular security-response cadence | **Is the fix version** for CVE-2026-48526 / CVE-2026-48524 |
| `opencv-python[-headless]==5.0.0.93` | MIT wrapper + Apache-2.0 core; headless wheel bundles LGPLv2.1 FFmpeg | Released 2026-07-02 | Active | None found for this version |
| `numpy==2.5.2` | BSD-3-Clause | Released 2026-08-09 | Active, large org/community backing | None found |
| `onnxruntime==1.28.0` | MIT | Current | Active — 1.28.0 is itself a hardening release | Signed-int/heap overflow fixes, CVE-2026-0994 protobuf bump — already applied |
| `exif==1.6.1` | MIT | Not archived | **Thin, not stalled**: solo maintainer, low bandwidth — real but slow responsiveness, distinct from `vobject`'s genuinely dead pace | None found |
| `python-magic==0.4.27` | MIT | No PyPI release since 2022-06-07 | **Confirmed genuinely latest, not neglect** — a small, feature-complete wrapper; quiet because finished, not abandoned mid-work | None found |
| `mysql-connector-python==26.7.0` | **GPL-2.0 + Oracle's Universal FOSS Exception — CONFIRMED VIOLATION** | Current (Oracle re-based versioning to track MySQL Server 9.7.0 → connector 26.7.0) | Active, Oracle-maintained | Prior CVE-2024-21272 long fixed; nothing against 26.7.0 |
| `psycopg[binary]>=3.3.4` | **LGPL-3.0 (binary variant) — CONFIRMED VIOLATION** | Current | Active | None found for psycopg3 itself |
| `argon2-cffi>=25.1.0` | MIT | Current | Active | None found |
| `redis>=8.1.0` (Python client) | MIT | Current | Active | None found (server-side Redis CVEs are separate, see Docker section) |
| `slowapi>=0.1.10` | MIT | Released 2026-06-13, ending a ~2-year gap since 0.1.9 | **Watch this one** — confirmed real, but the multi-year gap before this release is a slower cadence than the others in this table, worth re-checking at the next audit | None found |
| `httpx2>=2.10.0` (dev) | Same lineage as `httpx` | Current | **Confirmed legitimate, not a typosquat** — Pydantic took over stewardship of the original `httpx` project under this name; ~190M downloads/month, active | None found |
| `pytest>=9.1.1` (dev) | MIT | Released 2026-06-19 | Active | None found |

## Docker base images (`previous-work/multi-user-web-app/`)

| Image | Last activity | Activity pattern | CVE status |
| --- | --- | --- | --- |
| `python:3.12-slim` / `-slim-bookworm` | Rebuilt on Debian's own patch cadence | Actively rebuilt upstream | Usual Debian-package accumulation for this tag family, not uniquely broken — needs routine rebuilding |
| `caddy:2.11.4-alpine` | 2.11.4 is current | Active | **Is the fix version** for CVE-2026-45135 / CVE-2026-45692 |
| `redis:8.8-alpine` | 8.8 line current | Active upstream, but this project's own reference is a **floating minor tag** — see [GLOSSARY.md](../GLOSSARY.md) | Server CVEs (CVE-2026-25243 RESTORE RCE + siblings) fixed as of the 8.8 line — resolves patched today, but can silently regress without re-pull/digest-pin |
| `postgres:18.4-bookworm` | Released 2026-08-05 | Active | **Is the fix version** for CVE-2026-6477 / CVE-2026-6473 / CVE-2026-6476 |
| `boky/postfix@sha256:aafc...` | Old commits; described by its own ecosystem as "feature complete" | **The pattern to watch for, Docker version**: not abandoned exactly, but development has genuinely stopped, not just gone quiet between releases — legacy OpenDKIM baked in. At least digest-pinned, so reproducible even if stagnant | No open CVE tracked against the pinned digest, but a hardened Chainguard alternative exists |
| `ghcr.io/astral-sh/uv:latest` (build-stage `COPY --from`) | uv itself ships frequently | uv the tool is actively maintained — irrelevant to the risk here | **Flag: unpinned floating tag** — the exact binary copied into the build isn't reproducible/auditable regardless of how active uv's own releases are |

## Vendored AI model picks (`curation/DETECTORS.md`) — forward-looking, not yet integrated

None of these are wired into working code today — the pivot moved to a native Android app and
none of this pipeline has been ported on-device yet. Spot-checked against the known starting gaps:

- **YuNet** (face detection) — MIT claim **confirmed** against the actual `LICENSE` file in
  `opencv_zoo` (Shiqi Yu, 2020). Still valid, no change needed.
- **`age-gender-recognition-retail-0013`** (OpenVINO Open Model Zoo) — **another "recent push,
  different pattern" case**: repo is not archived/deleted (last push 2026-09-04, very recent), but
  its own README carries a "maintenance mode... see `openvino_notebooks` instead" banner — Intel is
  actively steering new users away from this repo without formally shutting it down. The last-push
  date alone would read as healthy; the actual pattern is "being wound down in practice." The model
  file itself is **confirmed still reachable**: both `.bin` (8.5MB) and `.xml` return HTTP 200 from
  `storage.openvinotoolkit.org` as of 2026-09-06, and `model.yml` still assigns Apache-2.0 + Intel
  copyright. No Hugging Face mirror exists for this specific model — it's single-sourced from
  Intel's own CDN, a real fragility to track, but nothing has rotted today. **No re-sourcing
  decision is forced.**
- **RTMPose / `mmpose#2106`** — **confirmed resolved**, matching the parallel session's claim
  exactly: maintainer `ly015` (GitHub role: MEMBER) replied 2023-03-21 that commercial use of the
  pretrained weights "should be allowed... you may need to consult legal experts for a definitive
  answer," issue closed with no further pushback. This project's existing treatment (fallback-only,
  not a co-pick, since RTMPose isn't the actual choice — MediaPipe Pose/BlazePose is) remains the
  right call; nothing to change.
- **FER+** (`emotion-ferplus-8`) — Apache-2.0 confirmed, `onnx/models` repo active (pushed
  2026-09-01), asset still present.
- **Open-NSFW2** — MIT confirmed via GitHub API (`spdx_id: MIT`), repo active (pushed 2026-08-29).

## Installed toolchain — dev machine and deployment target(s)

The sections above cover dependencies declared in a manifest (Gradle, pip/uv, a Dockerfile). This
section covers software installed directly on a machine, outside any project manifest — asked for
explicitly as part of this audit.

### Dev machine (Joakim's own) — compiled from what's already documented in this repo

- **Android Studio** — installed from the self-contained `.tar.gz` into Joakim's home directory
  (not a system package), per [POLICY.md](../policies/POLICY.md)'s no-system-wide-toolchain rule.
  Android SDK installed via Studio's own SDK Manager into `~/Android/Sdk`.
- **Gradle 8.14.5** — `android/gradlew` pins this exact version; a one-off Gradle install was used
  once to generate the wrapper itself.
- **JDK** — Android Studio bundles JBR 25, but Gradle 8.14.5's embedded Kotlin compiler crashes on
  it; builds actually run under a separate JBR 21 install at `~/.jdks/jbr-21.0.11`. Both exist on
  this machine.
- **Python** — no system `pip`/`venv` (missing `ensurepip`/`python3-venv`); `uv` is used instead,
  per-project, per [photo-server/TOOLCHAIN.md](../photo-server/TOOLCHAIN.md). `uv`'s own installed
  version/update channel wasn't checked this pass.
- **`.githooks/pre-commit`** — runs on every commit; already tracked as a local-code-execution
  surface in [THREATS.md](THREATS.md) row 7.

This list reflects what's already written down elsewhere in this repo — it is **not** a fresh scan
of the actual machine (no `dpkg -l` / `apt list --installed` / `pip list` / `uv --version` was run
against it this pass). Doing that is a real option but a separate judgment call — see "Open items"
below.

### Deployment server(s) — outside this audit's reach

- **No production server is currently live** for this pivoted architecture — `android/` is
  sideloaded only ([mobile/README.md](../mobile/README.md)), no server component.
  `previous-work/multi-user-web-app`'s `docker-compose.prod.yml` describes a target deployment
  shape for the now-superseded photo-server design, not a running system.
- A physical home server (`192.168.1.10`, behind an EdgeRouter X) is referenced in
  [POLICY.md](../policies/POLICY.md) and [THREATS.md](THREATS.md) rows 14-15, but its
  installed-package inventory lives in a **separate `hardware` repo**, outside this worktree and
  this session's visibility. This audit cannot enumerate what's installed there without either
  being pointed at that repo or a session run with access to that machine.

## Automated freshness/CVE-guard coverage — gap confirmed, worse than the starting assumption

Current `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/modules"
    schedule:
      interval: "weekly"
```

- **This entry currently monitors nothing** — `/modules` no longer exists in this repo; the pivot
  moved that code to `previous-work/`.
- This isn't an oversight of the pivot missing one update. Commit `dcaedeb` ("Archive
  app/server/detector/prototypes; start fresh on this branch") **deliberately deleted** five
  working ecosystem entries — `pip` for `/` and `/detector`, `uv` for `/server`, `docker` for `/`,
  `/server`, and `/detector` — rather than repointing them to their new `previous-work/` paths,
  leaving only the stale `pip`/`modules` entry behind.
- No entry exists for `previous-work/` (4 requirements.txt + 1 pyproject.toml + 3 Dockerfiles), for
  `tools/` (checked — no dependency manifest exists there, pure stdlib, nothing to cover), or for
  `android/` (dependabot.yml natively supports `package-ecosystem: "gradle"` — this is the
  confirmed Gradle/Android gap named at the start of this audit).

### Recommendation (not applied — config change, needs Joakim's go-ahead)

A working `dependabot.yml` would need, at minimum:

1. A `gradle` entry for `/android`.
2. Either repointed `pip`/`uv`/`docker` entries for `previous-work/multi-user-web-app` (root,
   `/detector`, `/server`) and the other `previous-work/*/requirements.txt` files, or a deliberate
   decision to skip re-adding coverage there given its superseded status — that scope call belongs
   to Joakim, not this audit.
3. Removal of the dead `/modules` entry either way.

## Open items needing Joakim's decision

1. **License-bar scope — resolved 2026-09-06**: Joakim confirmed the MIT/Apache-2.0-only bar
   applies to every dependency this project takes on, not just vendored AI model code/weights — now
   recorded in [POLICY.md](../policies/POLICY.md). This makes three **confirmed violations**, each
   needing its own remediation plan (not decided in this pass — replace, or document a deliberate,
   narrow exception):
   - `junit:junit:4.13.2` (EPL-1.0, `android/`, test-only) — the obvious next step, JUnit5/Jupiter,
     is **also EPL (2.0)**, so it isn't a compliant swap; a real MIT/Apache-2.0-licensed Android
     test framework needs its own research pass before anything gets replaced.
   - `psycopg[binary]>=3.3.4` (LGPL-3.0, `previous-work/multi-user-web-app/server`) — superseded,
     not deployed; lowest urgency of the three.
   - `mysql-connector-python==26.7.0` (GPL-2.0 + Oracle's FOSS exception,
     `previous-work/multi-user-web-app/prototypes/differentiate_pictures`) — also superseded, not
     deployed.
2. **Dependabot config** — see recommendation above; a real config change, not applied here.
3. **`io.getstream:photoview` staleness** — no better MIT/Apache-2.0 alternative currently known;
   recommend monitoring rather than replacing.
4. **Live system-inventory scan — resolved, not wanted (asked 2026-09-06)**: Joakim confirmed the
   documented toolchain state above is enough; no `dpkg -l`/`pip list`/`uv --version` scan was run
   against the real dev machine, and the separate `hardware` repo (`192.168.1.10` server) stays out
   of scope for this audit.

## Sources

Representative, not exhaustive — full URL lists are in each research pass's own transcript.
GitHub API (`archived`/`license`/commit metadata) for `GetStream/photoview-android`,
`chrisbanes/PhotoView` → `Baseflow/PhotoView`, `UweTrottmann/PhotoView`, `coil-kt/coil`,
`robolectric/robolectric`, `junit-team/junit4`, `android/android-test`,
`material-components/material-components-android`, `openvinotoolkit/open_model_zoo`, `onnx/models`,
`bhky/opennsfw2`; `api.osv.dev` (9 Android packages + Python packages); `pypi.org` JSON API
(`slowapi`, `python-magic`); release notes/changelogs for FastAPI, pytest, NumPy, ONNX Runtime,
Caddy, Redis, PostgreSQL 18.4, PyJWT, Pillow; `github.com/open-mmlab/mmpose/issues/2106`;
`storage.openvinotoolkit.org` (HTTP HEAD on model weights); `httpx2.pydantic.dev`;
`dev.mysql.com/doc/dev/connector-python/license`; `images.chainguard.dev/directory/boky-postfix`.

## Status

Audited 2026-09-06, three parallel research passes. Two passes' lookups logged to
`~/.claude/research_log.jsonl` per this project's research-log convention; the Android pass's
lookups failed to log due to worktree sandboxing on that subagent's side — not backfilled in this
pass since the write needs a permission prompt outside this repo while this session was
mid-task; flagged here as a small follow-up rather than silently dropped. Re-verify before relying
on specifics if this file is read long after this date — license/maintenance status moves.
