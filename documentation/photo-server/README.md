# photo-server/

The metadata-and-serving phase of the project: a small multi-user web
server so Elisabeth (and Joakim) can browse, search, tag into albums, and
download picks from photos already ingested onto this machine's ZFS pool.
Distinct from [../picture-handling/](../picture-handling/README.md) (the
existing single-machine, single-user Python sorting tool) and from
[../distributed-sync/](../distributed-sync/README.md) (future multi-device
P2P sync — not started, unaffected by this work).

Status: **Phase 0 done, Phase 1 (login) in progress on branch
`phase-1-login`.** 0.1–0.4 checkpointed (health check, Dockerfile +
compose, `users` table, fail-fast env config). Phase 1's architecture is
decided (see TODO.md's Phase 1 note): ported from Joakim's existing
login implementation in the sibling `buzzkit` repo, keeping buzzkit's
own argon2id choice (OWASP's current recommendation, and a change from
this doc's original bcrypt spec) and JWT access+refresh tokens backed
by a `redis` service for revocation (instead of TODO.md's original
plain Postgres-session fallback). 1.1–1.8 done and tested (hashing, CLI
account creation, login route, generic error, protected-route
dependency, token expiry, audit logging, IP-based rate limiting — 40
tests green). Next up is 1.9 (security pass: cookie-flag test, CSRF
confirmation, logout endpoint, `JWT_SECRET_KEY` length validator), then
1.10 (login page frontend, per MOCKUP.md) before 1.11's human
checkpoint. Two more roadmap gaps found and fixed along the way: TODO.md
originally had no step to build the login page itself (API-only) or,
further out, the lightbox/info-panel/search-panel screens named in
MOCKUP.md — those two are now marked **(blocked on spec)** since
MOCKUP.md only names them without the level of detail its own Login
screen section has. This folder
originally absorbed two external planning documents Joakim supplied in
chat — a build plan and a GUI spec amendment — into the repo's permanent
documentation, per [CLAUDE.md](../../CLAUDE.md)'s self-sufficiency rule.
Those two source documents were not kept as separate files here; their
content was distilled into the files below so there is one place to
read, not several competing drafts.

## Contents

| File | What's there |
| --- | --- |
| [TODO.md](TODO.md) | The build roadmap — small, ordered, TDD-first steps. Start here for "what's next." |
| [MOCKUP.md](MOCKUP.md) | Written spec for the first two screens (login, thumbnail grid) — no code yet |
| [DATA_DICTIONARY.md](DATA_DICTIONARY.md) | Full schema, which columns are live now vs reserved |
| [HARDWARE.md](HARDWARE.md) | The server this runs on |
| [DEFERRED.md](DEFERRED.md) | What's explicitly out of scope, and why |
| [TOOLCHAIN.md](TOOLCHAIN.md) | Local dev toolchain (uv) and testing against Postgres |

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
- Docker Compose, not a native install (see [HARDWARE.md](HARDWARE.md)
  for why). PostgreSQL is the only database engine; no separate search or
  vector store (tsvector now, pgvector later, same instance).
- Everything here inherits [POLICY.md](../policies/POLICY.md)'s privacy
  rule and CLAUDE.md's high-blast-radius list (deployment, schema
  changes, and running against the real photo library all require
  Joakim's sign-off, not just this file's say-so).

## Priority order

Login (TODO.md Phases 0–1) is being built **before** anything else in
this folder, including before the rest of the original build plan's
Phase A schema. Resolved (see Status above, decided before 1.1 was
built): Phase 1 adapts Joakim's existing buzzkit login implementation
rather than building fresh — this note used to pose that as an open
question for "the next session"; fixed 2026-07-17 since it had gone
stale, contradicting the file's own Status section above once the
decision was actually made and executed.

## Why the Sunday deadline

Elisabeth's mother is holding a memorial for Per, her late partner, on a
specific Sunday; she asked Joakim to rip a few of Per's CDs/DVDs of
pictures and movies so she can pick a handful to show on a picture-frame
USB stick there. That single, narrow need is the entire reason v1's
scope stops at "browse, search, tag into an album, download a zip" — see
[MOCKUP.md](MOCKUP.md) and [TODO.md](TODO.md).

## Relationship to the wider vision

This folder is one narrow, closed slice of a much larger system Joakim
is maturing over time — see [../VISION.md](../VISION.md)'s Pillar 2 for
the full metadata/curation direction this feeds into. Nothing here
should grow toward distributed storage, cross-household sharing, or
AI-driven curation suggestions without an explicit decision to do so;
those are separate, not-yet-scheduled pillars, not this folder's job.

This is also why Postgres was chosen as the sole database engine (see
"Non-negotiables" above) — no second database will be needed if/when
Pillar 2's on-device-inference direction reaches this folder.
