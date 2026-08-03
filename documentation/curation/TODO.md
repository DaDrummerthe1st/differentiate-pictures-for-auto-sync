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

## VPS — hardware audit + EU data-residency verification

Raised 2026-08-03. Joakim's VPS: `161.97.174.16`, a Contabo service, for possible V1 central hosting
(alongside the existing home box, [../photo-server/HARDWARE.md](../photo-server/HARDWARE.md)).

**Already confirmed this session, not guessed** — public RIPE RDAP lookup (`https://rdap.db.ripe.net/ip/161.97.174.16`),
no VPS access needed: the IP block (`161.97.160.0/20`) is RIPE-registered to **Contabo GmbH, Munich,
Germany, country code DE**; reverse DNS resolves to `vmi3146870.contaboserver.net`, Contabo's standard
naming. This is strong evidence the VPS is physically in Germany, but RIPE registration is the
*legal registrant's* country, not a cryptographic guarantee of the physical rack's location — Contabo's
own control panel (chosen at signup, e.g. "Contabo Germany") is the authoritative source and should
be checked directly, not assumed from this alone.

**Done 2026-08-03** — Joakim ran the command block and the Contabo control panel directly. Results,
recorded here provisionally (real central home is the `workstation` repo, still queued behind its own
concurrent session — see "Central hardware record" below):

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

**Comparison note vs. the home box** ([../photo-server/HARDWARE.md](../photo-server/HARDWARE.md)):
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

## Central hardware record — cross-repo, queued behind another session

Raised 2026-08-03: Joakim wants one central HW-info record across all machines (this project's home
box, this VPS, anything else), and it belongs in `/home/joakim/code/resources/workstation` — a
separate repo, not this one — where another Claude session is currently active. **Queued here, not
attempted**, to avoid a concurrent-edit collision. Once that repo is free: home-box HARDWARE.md
content and this VPS's audit results both migrate there, with a short pointer left in
[../photo-server/HARDWARE.md](../photo-server/HARDWARE.md) — mirrors that file's own
already-flagged-but-not-done "may belong outside this folder" note in
[../photo-server/DEFERRED.md](../photo-server/DEFERRED.md), just resolved to an external repo instead
of an internal move.

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

## First real test step, once one area is actually researched and picked

Not written yet — deliberately, per this project's TDD rule (a failing test before implementation,
every time) and its "high-blast-radius" rule (running anything against the real photo library needs
Joakim's go-ahead; only `resources/testpics`/disposable fixtures without asking first,
[../policies/WORKFLOW.md](../policies/WORKFLOW.md)). The shape once a model is picked: a failing test
asserting the chosen detector returns the expected structured output on one fixture image, then the
minimal wiring to pass it — same pattern as every phase in
[../photo-server/TODO.md](../photo-server/TODO.md). Don't skip ahead to this before an area has an
actual model pick.

## /tank test-data convention (noted, not a build item)

Confirmed 2026-08-02: `/tank/momfiles` stays Elisabeth's home folder, unchanged. Joakim's own scope
for testing against real (non-family-memorial) photos is the rest of `/tank`, outside `momfiles` —
no new mount/access mechanism needed, since Joakim already has full `/tank` access via his existing
sudo SSH account ([../photo-server/HARDWARE.md](../photo-server/HARDWARE.md)). Whatever test/prototype
code eventually reads real photos still needs to run **against `resources/testpics`
or other disposable fixtures without asking first** per the high-blast-radius rule above — running
against real `/tank` content (Joakim's own or otherwise) needs his go-ahead each time, same as it
already does for `momfiles`.

## Status

Opened 2026-08-02, alongside [README.md](README.md)/[ARCHITECTURE.md](ARCHITECTURE.md)/
[DETECTORS.md](DETECTORS.md). Nothing here is scheduled work yet — a catalog and an open-question
list, not numbered build steps.
