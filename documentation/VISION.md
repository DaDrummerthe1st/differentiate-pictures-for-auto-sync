# Vision — long-term system direction

Project-wide, like [policies/POLICY.md](policies/POLICY.md), but for
direction rather than hard rules. Captures the shape Joakim sees this
system maturing into over a long period, so a future session inherits it
instead of losing it. **None of this is committed design or scheduled
work** — only what's in a topic folder's `TODO.md` is actually being
built. This file exists so later phases build toward the right shape,
not to expand any current phase's scope.

## Current build vs. this vision

[photo-server/](photo-server/README.md) — the deliverable for a specific
Sunday memorial, see its README — is a deliberately narrow, **closed**
slice of Pillar 2 only: two known accounts, no data leaves the server,
no network sharing. None of the other three pillars are in scope for
that build.

## Pillar 1 — Distributed storage network (DFS)

Torrent-style distributed file system across users' own NAS devices;
each user's files stay encrypted, and contributing spare storage/compute
earns cloud storage/AI-compute credit elsewhere on the network, minus
overhead. Full description already lives in
[distributed-sync/README.md](distributed-sync/README.md) — not repeated
here.

## Pillar 2 — Metadata, search, and curation

Make it easy to find pictures by search criteria — this is what
photo-server/ builds first, narrowly, for one household. Longer-term:
the system suggests photos to remove, learned globally across the
network and personalized per user. See
[photo-server/DPFAS_VISION.md](photo-server/DPFAS_VISION.md) for the
on-device-inference direction this builds toward.

## Pillar 3 — Presentation and sharing

At an event — a party, up to something enormous — attendees take
pictures and share them with chosen people through the self-contained
network; this is the mechanism that brings in new users (interest,
registration). Event producers can build albums to find and display the
right pictures for the event. A user who opts to share all her pictures
is "premiered" — given more access from the network — in exchange for
giving it more information.

**Open tension, not resolved**: this opt-in-for-privilege model sits
against POLICY.md's "no data leaves the server" default for the current
closed build. These are two different trust boundaries — a closed
household server versus an opted-in sharing network — and any future
design must keep them explicitly separate so the closed default never
silently shifts. Tracked as an open question in
[policies/POLICY.md](policies/POLICY.md).

## Pillar 4 — Multi-angle event reconstruction

Future possibility: reconstruct a full "movie" of an event from the
separate angles/clips different attendees filmed at the same place and
time. Least defined of the four — no design yet, not even a rough one.

## Cross-cutting principle

As much of this as possible runs distributed across users' own NAS
hardware rather than centralized infrastructure — redundancy is what
keeps a cloud-saved file available even when its origin device is
offline.

## Status

All four pillars are open, none committed, none scheduled. Pillar 1's
timeline is the "full roadmap addendum... still pending from Joakim"
open question already tracked in
[distributed-sync/TODO.md](distributed-sync/TODO.md). Pillars 2–4 don't
have TODOs yet because nothing is being built against them.
