# photo-server/

The metadata-and-serving phase of the project: a small multi-user web
server so Elisabeth (and Joakim) can browse, search, tag into albums, and
download picks from photos already ingested onto this machine's ZFS pool.
Distinct from [../picture-handling/](../picture-handling/README.md) (the
existing single-machine, single-user Python sorting tool) and from
[../distributed-sync/](../distributed-sync/README.md) (future multi-device
P2P sync — not started, unaffected by this work).

Status: **planning only, no code written yet.** This folder absorbs two
external planning documents Joakim supplied in chat — a build plan and a
GUI spec amendment — into the repo's permanent documentation, per
[CLAUDE.md](../../CLAUDE.md)'s self-sufficiency rule. Those two source
documents are not kept as separate files here; their content is distilled
into the files below so there is one place to read, not several competing
drafts.

## Contents

| File | What's there |
| --- | --- |
| [TODO.md](TODO.md) | The build roadmap — small, ordered, TDD-first steps. Start here for "what's next." |
| [MOCKUP.md](MOCKUP.md) | Written spec for the first two screens (login, thumbnail grid) — no code yet |
| [DATA_DICTIONARY.md](DATA_DICTIONARY.md) | Full schema, which columns are live now vs reserved |
| [HARDWARE.md](HARDWARE.md) | The server this runs on |
| [DEFERRED.md](DEFERRED.md) | What's explicitly out of scope, and why |
| [DPFAS_VISION.md](DPFAS_VISION.md) | The longer-term metadata/inference direction this phase feeds into |

## Non-negotiables specific to this topic

- No photo or user data ever leaves the server. No cloud APIs, no
  telemetry. Sole exception: Let's Encrypt certificate issuance.
- Two accounts only: joakim.reuterborg@gmail.com (admin),
  elisabeth.reuterborg@gmail.com (member).
- Same subdomain (`photos.reuterborg.se`) serves both the browser UI and
  the JSON API, split by path prefix (`/api/*`) or `Accept` header —
  never user-agent sniffing.
- The root domain (`reuterborg.se`) already serves something that must
  keep working. Only ever touch the `photos.` subdomain, and double-check
  DNS changes don't affect the root (see TODO.md's HTTPS phase).
- Docker Compose, not a native install — see HARDWARE.md for why.
  PostgreSQL is the only database engine; no separate search or vector
  store (tsvector now, pgvector later, same instance).
- Everything here inherits [POLICY.md](../policies/POLICY.md)'s privacy
  rule and CLAUDE.md's high-blast-radius list (deployment, schema
  changes, and running against the real photo library all require
  Joakim's sign-off, not just this file's say-so).

## Priority order

Login (TODO.md Phases 0–1) is being built **before** anything else in
this folder, including before the rest of the original build plan's
Phase A schema. Joakim has an existing login implementation from another
project he'll bring to the next session — confirm whether Phase 1 adapts
that implementation or builds fresh per TODO.md's spec before writing any
auth code.
