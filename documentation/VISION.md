# Vision — long-term system direction

Project-wide, like [policies/POLICY.md](policies/POLICY.md), but for direction rather than hard rules. Captures the shape Joakim sees this system maturing into over a long period, so a future session inherits it instead of losing it. **None of this is committed design or scheduled work** — only what's in a topic folder's `TODO.md` is actually being built. This file exists so later phases build toward the right shape, not to expand any current phase's scope.

## Current build vs. this vision

[photo-server/](photo-server/README.md) — the deliverable for a specific Sunday memorial, see its README — is a deliberately narrow, **closed** slice of Pillar 2 only: two known accounts, no data leaves the server, no network sharing. None of the other three pillars are in scope for that build.

## Pillar 1 — Distributed storage network (DFS)

Torrent-style distributed file system across users' own NAS devices; each user's files stay encrypted, and contributing spare storage/compute earns cloud storage/AI-compute credit elsewhere on the network, minus overhead. Full description already lives in [distributed-sync/README.md](distributed-sync/README.md) — not repeated here.

**Foundation laid 2026-07-26** (see [upload-and-share/OWNERSHIP.md](upload-and-share/OWNERSHIP.md)): sharing a photo under "strict" terms is designed as a revocable, streamed, key-gated grant — the sharee's node may durably hold an encrypted piece (real redundancy contribution) without ever holding enough to view or reconstruct without the owner's live cooperation. A "free" share is the opposite: an irrevocable, full transfer of independent ownership. This resolves the credit-worthiness question concretely for strict shares (storing ciphertext for someone else is real, creditable contribution even though you can't see it) — the credit *mechanism* itself (how much, redeemed how) is still undefined. Evaluated against existing prior art rather than designed from nothing: Storj (erasure coding, no replication) and Filecoin (replication + on-chain proof) show the two main redundancy strategies; SyncThing was evaluated and rejected as a base to build *on* (no ownership/sharing/credit concept exists in it to reuse) but stays a candidate for raw device-to-device transport once a second real node exists.

## Pillar 2 — Metadata, search, and curation

The standing goal: get users to generate metadata around each photo's vectorized representation, through three UX paths — search/filter (what [photo-server/](photo-server/README.md) builds first, narrowly, for one household; see its DATA_DICTIONARY.md's Tag dimensions table for current status), manual tagging (schema now, endpoints fast-follow), and automated analysis via on-device face/object recognition (DPFAS phase, not started). Inference for that third path runs on the phone — only derived tags and, later, embeddings sync back to the server via pgvector, so raw photos never need to leave it. Longer-term: the system suggests photos to remove, learned globally across the network and personalized per user.

**Design principle, raised 2026-07-18**: every tagging/curation interaction the UX asks of a user should be *motivated* — the user should understand why they're being asked, not just be presented a blank tagging widget. The goal is more genuine human interaction with the photos themselves (looking, remembering, deciding), not tagging as a chore done to satisfy the system. Applies across all three UX paths above, including automated tags (blur/object/individual identification) once built — surface them as something the user reviews and confirms, not silently trusts.

## Pillar 3 — Presentation and sharing

At an event — a party, up to something enormous — attendees take pictures and share them with chosen people through the self-contained network; this is the mechanism that brings in new users (interest, registration). Event producers can build albums to find and display the right pictures for the event. A user who opts to share all her pictures is "premiered" — given more access from the network — in exchange for giving it more information.

**Open tension, not resolved**: this opt-in-for-privilege model sits against the closed-by-default posture required elsewhere — tracked as an open question in [policies/POLICY.md](policies/POLICY.md).

**Event/party mode, thoroughly discussed 2026-07-26** (full design: [upload-and-share/EVENTS.md](upload-and-share/EVENTS.md)): a host (wedding, funeral, birthday) generates a QR code that both invites uploads and auto-tags every photo contributed through it as belonging to that event — "do you have any pictures? upload them to us!" made concrete. Three independent axes, confirmed as separate rather than one combined preset: who may upload (free-for-all / pre-approved / register-then-approve), what invitees can see (every upload vs. a curated best-of, AI- and/or human-reviewed), and whether a live TV-screen wall displays the feed — any combination is possible. **Genuinely unresolved, flagged rather than guessed**: who owns a photo uploaded with no account at all (proposed: a claimable pending-owner record, same mechanism as the email-share invite, not yet confirmed), and the real legal reporting obligations this project likely takes on once true strangers can upload without identity verification (a lawyer question, not an engineering one). Venue hardware (whether the host needs a physical local device on-site vs. remote upload to her existing home NAS) is explicitly deferred to a later version, not designed now.

## Pillar 4 — Multi-angle event reconstruction

Future possibility: reconstruct a full "movie" of an event from the separate angles/clips different attendees filmed at the same place and time. Least defined of the four — no design yet, not even a rough one.

## Cross-cutting principle

As much of this as possible runs distributed across users' own NAS hardware rather than centralized infrastructure — redundancy is what keeps a cloud-saved file available even when its origin device is offline.

## Status

All four pillars are open, none committed, none scheduled. Pillar 1's timeline is the "full roadmap addendum... still pending from Joakim" open question already tracked in [distributed-sync/TODO.md](distributed-sync/TODO.md). Pillars 2–4 don't have TODOs yet because nothing is being built against them. **Exception, 2026-07-26**: Pillars 1 and 3 got a real design pass — see [upload-and-share/](upload-and-share/README.md) (per-user ownership, strict/free sharing terms, event/party mode). Still not scheduled work (no TODO.md steps yet) — a design pass, not a committed build.
