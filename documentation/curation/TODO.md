# TODO — curation

Open items, not designed or scheduled — captured so absence is a decision, not an oversight, per
this project's documentation-layout rule. **Start with [RESEARCH_QUEUE.md](RESEARCH_QUEUE.md)'s "Up
next" for what to actually pick up next** — this file is the durable why/detail behind each item,
not the reading order.

## Research cadence going forward

**One area from [DETECTORS.md](DETECTORS.md)'s catalog per session** (or a small tightly-related
cluster, e.g. blur+exposure+noise) — confirmed with Joakim 2026-08-02, correcting this session's own
opening approach of launching one large multi-area research pass. **Refined 2026-08-03**: even this
catalog and this file's own open-items list are too much to hold at once — see
[RESEARCH_QUEUE.md](RESEARCH_QUEUE.md), a one-item-at-a-time pointer file opened specifically to fix
that. Each area-session should produce: concrete model options (open-weight, self-hostable, CPU-only
— see [ARCHITECTURE.md](ARCHITECTURE.md)'s inherited constraints), a resource-cost estimate, an
output shape, and a pick — written into that row of DETECTORS.md, status flipped to `researched`.
**Explicit exception, 2026-08-05**: Joakim asked to research and document everything that comfortably
fits in one session (not exceeding token budget) rather than one area at a time — four areas closed
in that single session (group/co-presence, age/gender, OCR-in-frame, human action/pose), run as
parallel background research agents to keep the calling session's own context lean. Not a standing
change to the one-area-per-session default above — a one-off broadening confirmed for that session,
same "cherry-pick, no forced order" spirit as RESEARCH_QUEUE.md's own menu, just wider on that
occasion.

## VPS — hardware audit + EU data-residency verification

Raised 2026-08-03. Joakim's VPS: `161.97.174.16`, a Contabo service, for possible V1 central hosting
(alongside the existing home box, the `hardware` repo's `server/192.168.1.10/`).

**Already confirmed this session, not guessed** — public RIPE RDAP lookup (`https://rdap.db.ripe.net/ip/161.97.174.16`),
no VPS access needed: the IP block (`161.97.160.0/20`) is RIPE-registered to **Contabo GmbH, Munich,
Germany, country code DE**; reverse DNS resolves to `vmi3146870.contaboserver.net`, Contabo's standard
naming. This is strong evidence the VPS is physically in Germany, but RIPE registration is the
*legal registrant's* country, not a cryptographic guarantee of the physical rack's location — Contabo's
own control panel (chosen at signup, e.g. "Contabo Germany") is the authoritative source and should
be checked directly, not assumed from this alone.

**Done 2026-08-03** — Joakim ran the command block and the Contabo control panel directly. Results
below; the authoritative copy now lives in the `hardware` repo's `server/161.97.174.16/` (moved
2026-08-07), this table stays as the original research record.

| Component | Spec |
| --- | --- |
| Product | Contabo Cloud VPS 10 SSD |
| CPU | AMD EPYC (virtualized), 4 vCPUs, 1 socket, 4 cores/socket, 1 thread/core |
| RAM | 7.8Gi total, ~5.7Gi available at idle |
| Storage | 150G disk (`sda`), 149G partition at `/`, 20G used, 125G free |
| OS | Ubuntu 24.04.4 LTS (Noble Numbat) |
| Public IP | 161.97.174.16 (confirmed via `ifconfig.me`, matches — no NAT/proxy surprise) |
| Timezone | Europe/Berlin (CEST, +0200), NTP-synchronized |
| **Datacenter (Contabo control panel, authoritative)** | **"Hub Europe"** |

**EU data-residency: verified with a real source, not the RIPE inference alone.** Web-search-confirmed
(2026-08-03): Contabo's "Hub Europe" is a physical datacenter in **Lauterbourg, France** (French-German
border, near Strasbourg) — corrects, not just confirms, last session's RIPE-based inference (which
only showed the *registrant's* address, Contabo GmbH in Munich, Germany — a different thing from the
physical rack's location). Either way the requirement holds: **France, EU**, not outside Europe.
Sources: [Contabo Hub Europe datacenter — datacentermap.com](https://www.datacentermap.com/france/strasbourg/contabo-hub-europe-datacenter/), [Welcome to Hub Europe — Contabo Blog](https://contabo.com/blog/welcome-to-hub-europe-new-data-center-for-all-your-cloud-needs/).

**Comparison note vs. the home box** (the `hardware` repo's `server/192.168.1.10/`):
more vCPUs (4 vs. the i5-650's 2 cores/4 threads) on modern EPYC silicon, likely faster per-core
despite being virtualized, but less RAM (7.8GB vs. 16GB) and no ZFS pool/`/tank` — this VPS is compute,
not the photo storage. Real home-server-vs-VPS comparison for where V1's worker process runs is still
open, now with real numbers instead of "no specs at all."

## License-strictness decision — resolved 2026-08-03

**Answered directly**: MIT/Apache-2.0 only, going forward — tighter than
[../policies/POLICY.md](../policies/POLICY.md)'s general "prefer open, not an absolute ban" wording,
specifically for third-party ML model weights used in this project. Reasoning: Joakim wants
unrestricted commercial use, and [../VISION.md](../VISION.md)'s own V2/V3 rollout phases (each user
gets their own NAS; commercialize, sell NAS/routers; scale to "everyone") mean AGPL-3.0's network-use
clause (triggers once software is run as a network service others use, obligating full source
release) is a real future obligation, not a low risk unique to today's private single-household use.
DETECTORS.md's picks updated accordingly: NanoDet-Plus (was already the pick), Open-NSFW2 (was
NudeNet, AGPL), OpenCLIP ViT-B/32 (was MobileCLIP2, Apple's restrictive Sample Code License). **Still
open**: whether this MIT/Apache-2.0-only bar should be written into
[../policies/POLICY.md](../policies/POLICY.md) itself (as a specific sub-rule under "Vendor lock-in
and openness") rather than living only in curation/ docs — a real question since POLICY.md is meant
to hold every genuinely project-wide hard constraint in one place; not resolved here, since POLICY.md
edits weren't explicitly authorized this turn.

## Where research actually lives — resolved 2026-08-03

`~/.claude/research_log.jsonl` (global, cross-project, hook-enforced) logs **queries, domains, and a
short note per lookup** (122+ entries from this repo alone, verified) — it was never meant to hold the
full synthesized report a research pass produces. That gap is now closed properly: full raw
research-pass reports (every candidate considered, not just the picks, full source list) live in a
**new, separate, cross-project repo**, `/home/joakim/code/resources/research-findings` — not in this
repo, and not only in chat history/temp scratch files as before. This session's own background
agent's full vision-model survey is saved there as its first entry
(`entries/2026-08-02-lightweight-self-hostable-vision-model-survey.md`), cross-referencing back to
[DETECTORS.md](DETECTORS.md), which keeps only the distilled picks + reasoning, per this project's
lean-and-compact doc philosophy — the two intentionally don't duplicate each other's content.

## Object-detection timing benchmark (real numbers, not the research pass's estimates)

Raised 2026-08-03. DETECTORS.md's picks came with latency figures measured on newer/faster CPUs than
the i5-650 (or the VPS above, hardware still unconfirmed) — real, not guessed, numbers about actual
per-photo time need a real run once a model is integrated, not an estimate. **What this session did
find, real and sourced** (from this session's own logged research, see
[../GLOSSARY.md](../GLOSSARY.md) — no Raspberry Pi 3-specific benchmark exists publicly for any
model surveyed, only Pi 4/5 data): YOLOv5n ≈ 4-5 FPS on a Raspberry Pi 4 even quantized; YOLOv8n ≈ 12
FPS on a Pi 5 via the ncnn runtime specifically (the fastest runtime found for ARM), dropping to ≈ 2.6
FPS under thermal throttling. These are Pi-class numbers, not i5-650 numbers, and "per photo" scales
mainly with input *resolution* (these models run at reduced resolutions like 320px, not full-size),
not file size in MB — a real i5-650 (or VPS) measurement is a (human checkpoint) item once a model is
actually wired up, per [../policies/WORKFLOW.md](../policies/WORKFLOW.md)'s TDD/high-blast-radius
rules — not something to estimate further from here.

## ONNX Runtime telemetry — real finding, action item for whenever a model actually gets wired up

Raised 2026-08-05, checking whether DETECTORS.md's picks (most run on ONNX Runtime, e.g. RapidOCR)
are appropriate for this project's closed-by-default posture ([../policies/POLICY.md](../policies/POLICY.md)).
Confirmed via ONNX Runtime's own privacy doc: telemetry is **on by default in official Windows
builds**, sending trace data to Microsoft (via Windows' own TraceLogging API), subject to the OS's
own consent/GDPR handling — **not implemented for Linux builds**. This project's actual target
hardware (the i5-650 home box, the Contabo VPS) is Linux, so no live risk today, but this needs an
explicit, tested "telemetry disabled" check the moment any ONNX-based model is actually integrated —
never assumed clean by default — and stays a hard blocker if this project is ever deployed on
Windows. MediaPipe (the human-action/pose pick, DETECTORS.md area J) was also checked: multiple
sources confirm on-device-only inference (no frame data leaves the device), but a separate
framework-level telemetry channel wasn't independently confirmed either way — flagged as unverified,
not assumed clean, worth a dedicated check before this becomes a real dependency.

## Build plan — started 2026-08-07, Phase 0-2 done, Phase 3 onward is the next session's handoff

The first numbered, TDD-able build plan for automatic tagging (same phased/Security-line/human-
checkpoint format as [../photo-server/TODO.md](../photo-server/TODO.md)) now exists — see the full
plan (roster, category/value mappings, all phases) in this session's saved plan file
(`documentation/plans/lazy-jingling-robin.md`), and [../tags/SCHEMA.md](../tags/SCHEMA.md)'s "Now"
section for what's actually built. Phase 0-1 were this repo's previous session ("only do phase 0 and
1 in this session... leave VERY SHORT notes for me to initialize phase 2 in the next session");
Phase 2 is this session's own work, same "one phase, short handoff" cadence:

- **Phase 0, done**: role-based tag visibility (`member`/`admin`, `source='auto'` rows always
  shared) — JWT gained a `role` claim, `app/auth.py` gained `require_session_with_role`,
  `app/main.py`'s `GET /api/tags`/`GET /api/tags/values` apply the new visibility rule. Full test
  coverage in `server/tests/test_tokens.py`/`test_auth_routes.py`, `app/tests/test_auth.py`/
  `test_tags.py`.
- **Phase 1, done**: `detector/` — a new containerized FastAPI service (skeleton only, `GET /health`),
  wired into `docker-compose.yml` with no host port published, `mem_limit: 768m` (measured idle at
  ~34MB — real per-model usage still needs the benchmarking item below once Phase 2+ loads models).
  Build + `docker compose exec photo-viewer` reachability smoke-tested locally, then torn down
  (`docker compose down`) — nothing left running.
- **Phase 2, done**: `detector/quality.py` — `detect_blur` (variance of Laplacian), `detect_exposure`
  (mean luminance, returns `"overexposed"`/`"underexposed"`/`None`), `detect_monochrome` (mean HSV
  saturation), each a pure function over a `PIL.Image`, thresholds as named, env-overridable
  constants (`QUALITY_BLUR_VARIANCE_THRESHOLD`, `QUALITY_UNDEREXPOSED_MEAN_LUMINANCE`,
  `QUALITY_OVEREXPOSED_MEAN_LUMINANCE`, `QUALITY_MONOCHROME_SATURATION_THRESHOLD`). Wired behind a new
  `POST /detect` on the detector service (multipart image upload in, `{"tags": [{"category": "generic",
  "value": ..., "bbox_x/y/w/h": null}]}` out — same field shape as `app/main.py`'s `TagCreate`, so
  Phase 5's orchestration job can insert the response directly). TDD against synthetic PIL fixtures
  (checkerboards, not solid colors — a flat solid-color image is degenerate for the blur metric,
  always reading as maximally blurry, confirmed against real `detect_blur` output rather than
  assumed; that behavior is itself asserted by a named test, not hidden). Full suite:
  `detector/tests/test_quality.py`, `detector/tests/test_detect.py`. Real end-to-end smoke-tested
  against the built container image (`docker compose up -d detector`, a real synthetic JPEG POSTed to
  `/detect` from inside the container, matched unit-test predictions exactly), then torn down.
  Wrap-up sweep caught and fixed one real gap the same session: `/detect` had no upload-size cap —
  `MAX_UPLOAD_BYTES` (25MB default, env-overridable) now rejects an oversized body in capped chunks
  before a full read/decode is attempted, see [../security/THREATS.md](../security/THREATS.md) #16.
  Also caught mid-sweep: `pillow` was pinned to a stale 11.3.0 in both `requirements.txt` and
  `detector/requirements.txt` — bumped to 12.3.0 (current release, confirmed via PyPI), full suite
  re-verified green against it before pinning.

**Start at Phase 3 next session**: face detection (YuNet). Phases 4-7 after that (object/animal
detection/NanoDet-Plus, the `app/auto_tag.py` orchestration job idempotent on `source='auto'` rows, a
local smoke-test against `resources/test_pictures/` before touching the server, then written-not-run
`docker-compose.prod.yml`/deploy commands for Joakim to run against `/tank`) — model picks,
category/value mappings (`generic`/`people`/`objects`/`animals`), and the vendoring convention (fetch
once, commit under `detector/models/`, license noted) are already decided in the saved plan, don't
re-research them. Per this project's "high-blast-radius" rule
([../policies/WORKFLOW.md](../policies/WORKFLOW.md)), nothing runs against the real `/tank` library
until Joakim's explicit go-ahead — confirmed this session as its own written-not-run deploy step,
after a local smoke-test on this workstation first.

**Raised 2026-08-07, this session, two decisions now confirmed via AskUserQuestion**: once Phase 3/4
load real models, Joakim wants to *see* this workstation's real load while different models tag
photos (CPU/RAM per detector, not just the existing idle-container `mem_limit` guess) — feeds
directly into the already-open "object-detection timing benchmark" item below, now with an explicit
"show me the load" framing, not just a number. **Confirmed: session scope stays at Phase 2 this
session** (quality trio has near-zero CPU cost, so there's nothing meaningful to watch yet) — Phase
3/4's real ONNX models, and the load-observation work that goes with them, are next session's start,
not this one. Separately, once Phase 6's local checkpoint passes, Joakim wants to actually deploy to
the `.10` home server and watch it run there too, **with monitoring and thorough system-usage
logging** — a real new requirement for Phase 7's deploy step, not previously scoped (Phase 7 as
designed only ships a `docker-compose.prod.yml` block and copyable commands, no monitoring/logging
stack). **Confirmed: lightweight, not a full metrics stack** — periodic `docker stats` logging to a
file (cron or a small script), no new persistent service, per this project's resource-efficiency
constraint on the home box's modest hardware ([ARCHITECTURE.md](ARCHITECTURE.md)); Prometheus/Grafana
explicitly rejected as too much footprint for this. Neither the load-observation
tooling nor the `docker stats`-logging script has been written yet — a real build item for whichever
session reaches Phase 6/7, still deployed by Joakim himself per POLICY.md's deployment rule, never
run by an AI session directly against `.10`.

## /tank test-data convention (noted, not a build item)

Confirmed 2026-08-02: `/tank/momfiles` stays Elisabeth's home folder, unchanged. Joakim's own scope
for testing against real (non-family-memorial) photos is the rest of `/tank`, outside `momfiles` —
no new mount/access mechanism needed, since Joakim already has full `/tank` access via his existing
sudo SSH account (the `hardware` repo's `server/192.168.1.10/`). Whatever test/prototype
code eventually reads real photos still needs to run **against `resources/testpics`
or other disposable fixtures without asking first** per the high-blast-radius rule above — running
against real `/tank` content (Joakim's own or otherwise) needs his go-ahead each time, same as it
already does for `momfiles`.

## Status

Opened 2026-08-02, alongside [README.md](README.md)/[ARCHITECTURE.md](ARCHITECTURE.md)/
[DETECTORS.md](DETECTORS.md). **2026-08-07**: no longer just a catalog — the "Build plan" section
above is this folder's first numbered, TDD-able roadmap, Phase 0-2 done, Phase 3 the next session's
explicit starting point.
