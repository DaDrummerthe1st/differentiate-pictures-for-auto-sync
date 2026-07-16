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
