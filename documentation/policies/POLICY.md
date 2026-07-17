# Policy

Hard, project-wide constraints. This is the one file where "hard rules
live here" — nothing project-wide should be duplicated in another doc.
For the general working agreement (how sessions operate, commit rules,
high-blast-radius definition), see [CLAUDE.md](../../CLAUDE.md).

## Privacy and safety

- Applies to every change, not just ones that look security-related
  (see CLAUDE.md's "Security and privacy first" rule).
- This app extracts and stores EXIF/GPS metadata from personal photos
  (see `app/gpsdata.py`). Location data is sensitive by default — never
  transmit, log, or expose it more broadly than the feature being built
  strictly requires.
- The planned distributed-sync/shared-storage feature (see
  [../distributed-sync/README.md](../distributed-sync/README.md)) means
  this project will eventually hold other people's files and metadata on
  infrastructure the user partially controls, and vice versa. Any design
  work in that area must treat "whose data is this, and who can see it"
  as a first-class question, not an afterthought — even before the
  architecture is finalized.
- **No browser `localStorage` for any frontend state** (Joakim, explicit,
  2026-07-17). If a UI preference or choice needs to persist, it belongs
  server-side (a `users`-table column, a cookie backed by the existing
  session, or similar) — under the account's control and subject to the
  same access/audit posture as everything else, not sitting unmanaged in
  the browser. Applies to every frontend feature, not just the one this
  was raised about (a recurring download-folder-picker prompt).

## Resource efficiency

- **Hard constraint (2026-07-17), not a preference**: all code must stay
  resource-tight — CPU, RAM, and disk. Reason: the target hardware isn't
  just today's server (HARDWARE.md) — this is meant to eventually run on
  genuinely constrained devices, Joakim's own example being a Raspberry
  Pi 3 (1GB RAM, ARM, no meaningful CPU headroom). Code that's "fine" on
  a beefy dev machine or even today's server can be a hard blocker
  there. Applies to every choice, not just ones that look
  performance-related: dependency picks (prefer lean deps over heavy
  ones for equivalent functionality), algorithms (avoid loading full
  datasets into memory when streaming/chunking works), container sizing
  (`mem_limit`s should reflect genuine need, not headroom-for-its-own-
  sake), and image processing specifically (this project already does
  Pillow-based thumbnail generation — CPU/memory-heavy per call by
  nature; cache aggressively, don't regenerate needlessly).
- Not yet done: an actual resource budget per target device (e.g. "must
  run the full stack under 1GB RAM on ARM") — until that's defined,
  treat "tight" as a design bias to apply on every change, not a
  measurable gate to check against. Define the real budget once there's
  a concrete Pi-class target to test against, not before.

## Licensing

- No open-source license has been chosen yet. Treat this as a private,
  personal project. Do not add a `LICENSE` file or make licensing claims
  until Joakim decides otherwise.

## Deployment and system access

- The AI session has no sudo access on the development machine and must
  never attempt system-level installs (Docker, database servers, network
  configuration, NAS OS setup, etc.). Such steps are always handed to
  Joakim as copyable commands.
- Deployment — of any kind, to any target — is always performed by
  Joakim, never automated by the AI session.

## Open questions

- **Closed vs. opt-in-sharing trust boundary**: the long-term vision
  (see [../VISION.md](../VISION.md) Pillar 3) includes a future mode
  where a user opts to share more of her data with the wider network in
  exchange for more from it. This must never be allowed to blur the
  current closed-by-default posture (no photo/user data ever leaves the
  server) — any future design needs an explicit, separate opt-in, not a
  gradual default shift. Unresolved; no design yet.
- Everything else tracked in each topic folder's `TODO.md` — see
  [../distributed-sync/TODO.md](../distributed-sync/TODO.md) for the
  current open item there.
