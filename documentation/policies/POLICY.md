# Policy

Hard, project-wide constraints. This is the one file where "hard rules live here" — nothing project-wide should be duplicated in another doc. For the general working agreement (how sessions operate, commit rules, high-blast-radius definition), see [CLAUDE.md](../../CLAUDE.md).

## Privacy and safety

- Applies to every change, not just ones that look security-related (see CLAUDE.md's "Security and privacy first" rule).
- This app extracts and stores EXIF/GPS metadata from personal photos (see `app/gpsdata.py`). Location data is sensitive by default — never transmit, log, or expose it more broadly than the feature being built strictly requires.
- **Closed-by-default (project-wide)**: no photo or user data ever leaves the server the user controls. No cloud APIs, no telemetry. Applies to every topic folder, not just photo-server (whose own README.md states this same rule for its scope — this is the source of truth it inherits from). Sole exception: Let's Encrypt certificate issuance for HTTPS.
- The planned distributed-sync/shared-storage feature (see [../distributed-sync/README.md](../distributed-sync/README.md)) means this project will eventually hold other people's files and metadata on infrastructure the user partially controls, and vice versa. Any design work in that area must treat "whose data is this, and who can see it" as a first-class question, not an afterthought — even before the architecture is finalized.

## Resource efficiency

- **Hard constraint (2026-07-17), not a preference**: all code must stay resource-tight — CPU, RAM, and disk. Reason: the target hardware isn't just today's server (HARDWARE.md) — this is meant to eventually run on genuinely constrained devices, Joakim's own example being a Raspberry Pi 3 (1GB RAM, ARM, no meaningful CPU headroom). Code that's "fine" on a beefy dev machine or even today's server can be a hard blocker there. Applies to every choice, not just ones that look performance-related: dependency picks (prefer lean deps over heavy ones for equivalent functionality), algorithms (avoid loading full datasets into memory when streaming/chunking works), container sizing (`mem_limit`s should reflect genuine need, not headroom-for-its-own-sake), and image processing specifically (this project already does Pillow-based thumbnail generation — CPU/memory-heavy per call by nature; cache aggressively, don't regenerate needlessly).
- Not yet done: an actual resource budget per target device (e.g. "must run the full stack under 1GB RAM on ARM") — until that's defined, treat "tight" as a design bias to apply on every change, not a measurable gate to check against. Define the real budget once there's a concrete Pi-class target to test against, not before.

## Licensing

- No open-source license has been chosen yet. Treat this as a private, personal project. Do not add a `LICENSE` file or make licensing claims until Joakim decides otherwise.

## Vendor lock-in and openness

- **Standing principle (2026-07-18), not an absolute ban**: prefer open, non-proprietary, vendor-neutral tools and formats over ones from a single controlling company, even when the proprietary option is technically stronger — Joakim's reasoning: lock-in shows up regardless of a vendor's short- or long-term intent, and openness itself is the better trade even on pure UX/cost/control grounds, not just an ethical stance. Concretely: when a technology choice has a genuinely open, vendor-neutral alternative (e.g. Selenium vs. Microsoft-driven Playwright, an open dependency vs. a proprietary SaaS), default to the open one and name the trade-off explicitly if going proprietary anyway — don't default silently to whichever tool is best-known or easiest to reach for.
- **Not absolute**: this repo already depends on GitHub (Microsoft-owned) for hosting - Joakim is aware and has independence plans (own VPS, own git server) already in motion, not a contradiction to resolve today. The principle guides new choices going forward; it doesn't mandate ripping out everything already in place.
- Directly affects an open decision right now: Playwright (Microsoft) vs. Selenium (W3C standard, no single owner) for this project's first frontend test harness — see `gui/TODO.md`. Apply this principle when that gets decided, don't re-litigate the philosophy each time a similar choice comes up.

## Deployment and system access

- The AI session has no sudo access on the development machine and must never attempt system-level installs (Docker, database servers, network configuration, NAS OS setup, etc.). Such steps are always handed to Joakim as copyable commands.
- Deployment — of any kind, to any target — is always performed by Joakim, never automated by the AI session.
- **Hard constraint (2026-07-18): no toolchain gets installed system-wide on the dev machine, by Joakim or by the AI session — containers or per-project virtualenvs only.** Not just "the AI can't run the installer" (the point above) — Joakim doesn't want it run system-wide either, even by his own hand. Applies to every language's tooling (Python already follows this via `uv`'s per-project `.venv`, see `TOOLCHAIN.md`; the same bar applies to Node/npm, browser-automation tools, and anything else this project ever adds) and to existing code too, not just new work — retrofit when touched, don't grandfather it in. When a tool ships an official container image (e.g. Playwright's `mcr.microsoft.com/playwright`), prefer that over a host install even if it means an extra `docker run`/`docker build` step.

## Open questions

- **Closed vs. opt-in-sharing trust boundary**: the long-term vision (see [../VISION.md](../VISION.md) Pillar 3) includes a future mode where a user opts to share more of her data with the wider network in exchange for more from it. This must never be allowed to blur the current closed-by-default posture (no photo/user data ever leaves the server) — any future design needs an explicit, separate opt-in, not a gradual default shift. Unresolved; no design yet.
- Everything else tracked in each topic folder's `TODO.md` — see [../distributed-sync/TODO.md](../distributed-sync/TODO.md) for the current open item there.
