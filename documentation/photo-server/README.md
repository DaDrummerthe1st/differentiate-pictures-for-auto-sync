# photo-server/

The metadata-and-serving phase of the project: a small multi-user web server so Elisabeth (and Joakim) can browse, search, tag into albums, and download picks from photos already ingested onto this machine's ZFS pool. Distinct from [../picture-handling/](../picture-handling/README.md) (the existing single-machine, single-user Python sorting tool) and from [../distributed-sync/](../distributed-sync/README.md) (future multi-device P2P sync — not started, unaffected by this work).

**Status (2026-07-19, end of session): live and working, production redeployed and current.** Elisabeth can log in and browse at `https://photos.reuterborg.se` (branch `mamma-photo-viewer`). Since 2026-07-18: a full outage (aging switch, not the server — see `bugs/solved/`), a since-fixed publicly-exposed Swagger/OpenAPI docs vulnerability, the Postgres schema-init + `Dockerfile` fixes, single-album view + DOM-unload of inactive albums, and the thumbnail silent-refresh fix below are all live in production.

**Open, real problems** (each its own file in `bugs/reports/`, no index kept - browse that folder directly, each file's `Status:` line says where it stands): Redis has no persistent volume (every container restart silently logs out every active session); the lightbox shows wrong/no content when clicking a not-yet-loaded thumbnail (not yet root-caused); a picture click intermittently fails to show after less than 5 minutes, other albums' thumbnails fine (2026-07-19, investigating). Fixed since 2026-07-18: Swagger docs public exposure, thumbnail/lightbox `<img>` tags having no silent-refresh on an expired access token (both **fixed**, see `bugs/solved/`).

**Starting a new session on this topic?** Don't re-derive today's history from scratch: `DEPLOYMENT.md` has the current, correct deploy steps; `HARDWARE.md` now documents the switch between the server and router; [POLICY.md](../policies/POLICY.md) has a hard resource-efficiency constraint and (added today) a no-system-wide-installs, containers/venvs-only constraint; `CHANGELOG.md`'s 2026-07-17 and 2026-07-18 entries have the complete blow-by-blow if you need it, but shouldn't be required reading to start working.

Not yet done, lower priority than the open items in `bugs/reports/`: 1.9a–c (admin password reset), 1.11's human checkpoint, and the `master`/`phase-1-login`/`mamma-photo-viewer` branch reunification (deliberately deferred — see TODO.md's "Branch relationship" section). This folder originally absorbed two external planning documents Joakim supplied in chat — a build plan and a GUI spec amendment — into the repo's permanent documentation, per [CLAUDE.md](../../CLAUDE.md)'s self-sufficiency rule. Those two source documents were not kept as separate files here; their content was distilled into the files below so there is one place to read, not several competing drafts.

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

- Inherits [POLICY.md](../policies/POLICY.md)'s closed-by-default rule: no photo or user data ever leaves the server.
- Two accounts only: joakim.reuterborg@gmail.com (admin), elisabeth.reuterborg@gmail.com (member).
- Same subdomain (`photos.reuterborg.se`) serves both the browser UI and the JSON API, split by path prefix (`/api/*`) or `Accept` header — never user-agent sniffing.
- The root domain (`reuterborg.se`) already serves something that must keep working. Only ever touch the `photos.` subdomain, and double-check DNS changes don't affect the root (see TODO.md's HTTPS phase).
- Docker Compose, not a native install (see [HARDWARE.md](HARDWARE.md) for why). PostgreSQL is the only database engine; no separate search or vector store (tsvector now, pgvector later, same instance).
- Everything here inherits [POLICY.md](../policies/POLICY.md)'s privacy rule and CLAUDE.md's high-blast-radius list (deployment, schema changes, and running against the real photo library all require Joakim's sign-off, not just this file's say-so).

## Priority order

Login (TODO.md Phases 0–1) is being built **before** anything else in this folder, including before the rest of the original build plan's Phase A schema. Resolved (see Status above, decided before 1.1 was built): Phase 1 adapts Joakim's existing buzzkit login implementation rather than building fresh — this note used to pose that as an open question for "the next session"; fixed 2026-07-17 since it had gone stale, contradicting the file's own Status section above once the decision was actually made and executed.

## Why the Sunday deadline

Elisabeth's mother is holding a memorial for Per, her late partner, on a specific Sunday; she asked Joakim to rip a few of Per's CDs/DVDs of pictures and movies so she can pick a handful to show on a picture-frame USB stick there. That single, narrow need is the entire reason v1's scope stops at "browse, search, tag into an album, download a zip" — see [MOCKUP.md](MOCKUP.md) and [TODO.md](TODO.md).

## Relationship to the wider vision

This folder is one narrow, closed slice of a much larger system Joakim is maturing over time — see [../VISION.md](../VISION.md)'s Pillar 2 for the full metadata/curation direction this feeds into. Nothing here should grow toward distributed storage, cross-household sharing, or AI-driven curation suggestions without an explicit decision to do so; those are separate, not-yet-scheduled pillars, not this folder's job.

This is also why Postgres was chosen as the sole database engine (see "Non-negotiables" above) — no second database will be needed if/when Pillar 2's on-device-inference direction reaches this folder.
