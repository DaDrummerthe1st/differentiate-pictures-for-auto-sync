# Vision — long-term system direction

Project-wide, like [policies/POLICY.md](policies/POLICY.md), but for direction rather than hard rules. Captures the shape Joakim sees this system maturing into over a long period, so a future session inherits it instead of losing it. **None of this is committed design or scheduled work** — only what's in a topic folder's `TODO.md` is actually being built. This file exists so later phases build toward the right shape, not to expand any current phase's scope.

## Current build vs. this vision

[photo-server/](photo-server/README.md) — the deliverable for a specific Sunday memorial, see its README — is a deliberately narrow, **closed** slice of Pillar 2 only: two known accounts, no data leaves the server, no network sharing. None of the other three pillars are in scope for that build.

**Reaffirmed 2026-07-27, generalized beyond just that one build**: this applies to *every* current design thread, not only photo-server specifically — [tags/](tags/README.md), [upload-and-share/](upload-and-share/README.md), all of it. The single VPS is the sole source of truth for all current work; nothing in today's design should assume or route through Pillar 1's DFS. Pillar 1 is a real, active pillar of this vision — not necessarily distant on the calendar — but it is not part of the current design phase, and no current schema/UX decision should be shaped around it prematurely. `distributed-sync/TODO.md`'s open questions (including the metadata-placement one raised this session) are legitimate to capture there for later, but nothing about them constrains work happening now.

## Pillar 1 — Distributed storage network (DFS)

Torrent-style distributed file system across users' own NAS devices; each user's files stay encrypted, and contributing spare storage/compute earns cloud storage/AI-compute credit elsewhere on the network, minus overhead. Full description already lives in [distributed-sync/README.md](distributed-sync/README.md) — not repeated here.

**Ownership groundwork laid 2026-07-26** (see [upload-and-share/OWNERSHIP.md](upload-and-share/OWNERSHIP.md)) — **deliberately scoped to one server, not this pillar's network**: a photo's "strict" (revocable, view-only) vs. "free" (irrevocable, full transfer) sharing terms are designed and reserved in schema now, enforced today as a plain live permission check with no second node involved. The real open tension this pillar will eventually have to resolve — a revocable strict share vs. sharees' hardware contributing durable, creditable storage — is named in that doc but explicitly **not designed there**; it stays this pillar's problem, unstarted. Prior art already checked for when that design happens: Storj (erasure coding, no replication) and Filecoin (replication + on-chain proof) for the redundancy/credit trade-off; SyncThing, rejected as a base to build *on* (no ownership/sharing/credit concept in it to reuse) but a candidate for raw device-to-device transport once a second real node exists.

## Pillar 2 — Metadata, search, and curation

The standing goal: get users to generate metadata around each photo's vectorized representation, through three UX paths — search/filter (what [photo-server/](photo-server/README.md) builds first, narrowly, for one household), manual tagging (the concrete category model: [tags/TAXONOMY.md](tags/TAXONOMY.md)), and automated analysis via on-device face/object recognition (DPFAS phase, not started). Inference for that third path runs on the phone — only derived tags and, later, embeddings sync back to the server via pgvector, so raw photos never need to leave it. Longer-term: the system suggests photos to remove, learned globally across the network and personalized per user. **Given a real design pass 2026-08-02**: see [curation/](curation/README.md) for the detector/embedding-index/Curator architecture behind that longer-term goal, and a refinement of "runs on the phone" into a concrete PWA-in-browser step after the current central-server phase, rather than a native app — not edited into this paragraph directly since curation/ is the more specific, later-dated source for that detail.

**Design principle, raised 2026-07-18**: every tagging/curation interaction the UX asks of a user should be *motivated* — the user should understand why they're being asked, not just be presented a blank tagging widget. The goal is more genuine human interaction with the photos themselves (looking, remembering, deciding), not tagging as a chore done to satisfy the system. Applies across all three UX paths above, including automated tags (blur/object/individual identification) once built — surface them as something the user reviews and confirms, not silently trusts.

## Pillar 3 — Presentation and sharing

At an event — a party, up to something enormous — attendees take pictures and share them with chosen people through the self-contained network; this is the mechanism that brings in new users (interest, registration). Event producers can build albums to find and display the right pictures for the event. A user who opts to share all her pictures is "premiered" — given more access from the network — in exchange for giving it more information.

**Open tension, not resolved**: this opt-in-for-privilege model sits against the closed-by-default posture required elsewhere — tracked as an open question in [policies/POLICY.md](policies/POLICY.md).

**Event/party mode, thoroughly discussed 2026-07-26** (full design: [upload-and-share/EVENTS.md](upload-and-share/EVENTS.md)): a host (wedding, funeral, birthday) generates a QR code that both invites uploads and auto-tags every photo contributed through it as belonging to that event — "do you have any pictures? upload them to us!" made concrete. Three independent axes, confirmed as separate rather than one combined preset: who may upload (free-for-all / pre-approved / register-then-approve), what invitees can see (every upload vs. a curated best-of, AI- and/or human-reviewed), and whether a live TV-screen wall displays the feed — any combination is possible. **Genuinely unresolved, flagged rather than guessed**: who owns a photo uploaded with no account at all (proposed: a claimable pending-owner record, same mechanism as the email-share invite, not yet confirmed), and the real legal reporting obligations this project likely takes on once true strangers can upload without identity verification (a lawyer question, not an engineering one). Venue hardware (whether the host needs a physical local device on-site vs. remote upload to her existing home NAS) is explicitly deferred to a later version, not designed now.

## Pillar 4 — Multi-angle event reconstruction

Future possibility: reconstruct a full "movie" of an event from the separate angles/clips different attendees filmed at the same place and time. Least defined of the four — no design yet, not even a rough one.

## Rollout phases — when and for whom

Distinct from the four Pillars above, which describe *what* gets built — this is Joakim's own three-version plan for *when* and *for whom*, folded in from [income/TODO.md](income/TODO.md) 2026-07-29:

- **V1**: a service for 2-3 people, mostly to observe *how* they actually use it — naming pictures, sharing outside the group, marking people/objects, etc. Also runs and saves AI model output on every picture: object detection, picture quality, venue guessing, feelings/emotions.
- **V2**: those 2-3 people each get their own NAS/router. Day-to-day experience stays unchanged — Pillar 1's DFS work happens behind the scenes. This is where centralization-vs-decentralization and load-balancing decisions actually get built, not before.
- **V3**: commercialize — sell NAS/routers, keep developing the system. Needs slow, organic growth to find/fix problems, since the overhead budget at this stage will be very small if any exists at all.
- **Long-term scale, explicitly not a small family-style network**: the stated goal is a service used by "everyone," concrete example — an AI curating the best photos/a photo-flow from an audience of 65,000 people at a large public event (ties to Pillar 3's event/party mode above). **Resolved 2026-07-29**: this doesn't mean cross-network face-matching needs a harder mechanism at that scale — see [distributed-sync/METADATA.md](distributed-sync/METADATA.md), access, not scale, is what bounds that search.

## Cross-cutting principle

As much of this as possible runs distributed across users' own NAS hardware rather than centralized infrastructure — redundancy is what keeps a cloud-saved file available even when its origin device is offline.

## Status

All four pillars are open, none committed, none scheduled. Pillar 1's timeline is the "full roadmap addendum... still pending from Joakim" open question already tracked in [distributed-sync/TODO.md](distributed-sync/TODO.md). Pillars 2–4 don't have TODOs yet because nothing is being built against them. **Exception, 2026-07-26**: Pillars 1 and 3 got a real design pass — see [upload-and-share/](upload-and-share/README.md) (per-user ownership, strict/free sharing terms, event/party mode). Still not scheduled work (no TODO.md steps yet) — a design pass, not a committed build.
