# photo-server/

The metadata-and-serving phase of the project: a small multi-user web
server so Elisabeth (and Joakim) can browse, search, tag into albums, and
download picks from photos already ingested onto this machine's ZFS pool.
Distinct from [../picture-handling/](../picture-handling/README.md) (the
existing single-machine, single-user Python sorting tool) and from
[../distributed-sync/](../distributed-sync/README.md) (future multi-device
P2P sync — not started, unaffected by this work).

Status (2026-07-17): **Live, deployed, and confirmed working end-to-end**
at `https://photos.reuterborg.se` on branch `mamma-photo-viewer`, built
under a same-day hard deadline (Elisabeth needed real access by 14:00 or
the fallback was a hand-delivered zip — see CHANGELOG). Real login
confirmed (not just reachability) after finding and fixing two
deploy-path gaps along the way — the production Postgres schema was
never initialized, and `server/Dockerfile` never copied `scripts/` in —
both tracked in [documentation/bugs/TODO.md](../bugs/TODO.md), both now
documented as required steps in [DEPLOYMENT.md](DEPLOYMENT.md) so a
fresh deploy won't rediscover them. Thumbnails were failing under
concurrent load (likely the container's memory limit vs. Pillow's
transient decode/resize spikes) — mitigated (`mem_limit` raised) and
partially fixed (a concurrency-limiting semaphore, TDD'd); a full
architectural fix (background/async generation) is the next real step,
see `bugs/TODO.md`. New standing structure from this deploy: a
`documentation/bugs/` tracking system (untriaged list + per-bug
investigation reports), a hard resource-efficiency policy in
[POLICY.md](../policies/POLICY.md) (this must eventually run on
Pi-class hardware, not just today's server), and a Troubleshooting
playbook in DEPLOYMENT.md. Not yet done: 1.9a–c (admin password reset),
1.11's human checkpoint, the `master`/`phase-1-login`/`mamma-photo-viewer`
branch reunification (deliberately deferred — TODO.md), and everything
in `bugs/TODO.md`. This folder
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
