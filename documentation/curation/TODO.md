# TODO — curation

Open items, not designed or scheduled — captured so absence is a decision, not an oversight, per
this project's documentation-layout rule.

## Research cadence going forward

**One area from [DETECTORS.md](DETECTORS.md)'s catalog per session** (or a small tightly-related
cluster, e.g. blur+exposure+noise) — confirmed with Joakim 2026-08-02, correcting this session's own
opening approach of launching one large multi-area research pass. Each area-session should produce:
concrete model options (open-weight, self-hostable, CPU-only — see
[ARCHITECTURE.md](ARCHITECTURE.md)'s inherited constraints), a resource-cost estimate, an output
shape, and a pick — written into that row of DETECTORS.md, status flipped to `researched`.

## Next session should start with

- **License decisions on this session's already-researched picks** (DETECTORS.md): object detection
  (NanoDet-Plus, Apache-2.0 vs. YOLO26n, AGPL-3.0), NSFW detection (NudeNet, AGPL-3.0 vs. Open-NSFW2,
  permissive), and the CLIP embedding backbone (MobileCLIP2, Apple's restrictive Sample Code License
  vs. OpenCLIP/SigLIP, MIT/Apache-2.0) all need a real call from Joakim before integration — the
  research picked the strongest option per axis (smallest/fastest vs. most permissive), not a single
  final answer.
- **VPS specs** — [ARCHITECTURE.md](ARCHITECTURE.md)'s rollout-phases section flags that no VPS specs
  exist anywhere in this repo, blocking a real home-server-vs-VPS comparison for where V1's worker
  process runs. Ask Joakim for the specs, or confirm a VPS isn't actually on the table yet.
- **Age/gender estimation's privacy flag** (DETECTORS.md, area B) — needs a real GDPR "special
  category" biometric-data read before it's researched as a model-pick item, not just queued
  alongside the others.
- **OCR/text-in-frame's privacy flag** (DETECTORS.md, area D) — same treatment: a photographed
  document/ID card is sensitive content this project hasn't reasoned about yet.
- **Weather-at-time-of-capture's policy flag** (DETECTORS.md, area G) — likely excluded outright by
  closed-by-default/no-cloud-APIs unless a fully offline historical-weather dataset exists; confirm
  before spending research time on it.

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
