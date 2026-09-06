# Vision — long-term system direction

Project-wide, like [policies/POLICY.md](policies/POLICY.md), but for direction rather than hard rules. Captures the shape Joakim sees this system maturing into over a long period, so a future session inherits it instead of losing it. **None of this is committed design or scheduled work** — only what's in a topic folder's `TODO.md` is actually being built. This file exists so later phases build toward the right shape, not to expand any current phase's scope.

## Core differentiator — raised 2026-08-05

Not the picture-handling itself — search, tagging, sharing are what every photo app does. What
sets this system apart is **complete, granular user control over what's shared and with whom**,
extending eventually to **what metadata even reaches a central point at all**, once each user has
her own physical space (Pillar 1) rather than a household sharing one server. Joakim's own framing,
worth keeping verbatim: the goal is a world where **"your privacy depends on the strength of your
password," not "your privacy is what we'll tell it to be"** — contrasting a self-hosted, user-held-key
model against a third-party platform (his example: Google/OAuth) that can unilaterally redefine what
"private" means. This isn't a new design decision so much as the thesis several already-made ones
serve: [policies/AUTHENTICATION.md](policies/AUTHENTICATION.md)'s no-third-party-OAuth rule,
[policies/POLICY.md](policies/POLICY.md)'s closed-by-default posture, and
[security/TODO.md](security/TODO.md)'s EDPB-Opinion-11/2024 finding that only subject-held-key storage
is GDPR-compatible — all mechanisms that put the key, and therefore the privacy, in the user's own
hands rather than an operator's. Every granular tag-visibility/sharing/circle mechanism designed in
[tags/](tags/README.md) is this principle applied at the data-model level, not a separate feature set.

**The system should help the user in any way it can, raised 2026-08-05** — not just via structured tagging/sharing controls above, but a genuine, standing channel for whatever a user wants to say that doesn't fit a tag: a bug, a wish, a question. First concrete mechanism: a free-text feedback channel, security considerations included from the start rather than bolted on — design sketch in [photo-server/DEFERRED.md](photo-server/DEFERRED.md), threat analysis in [security/THREATS.md](security/THREATS.md) #13.

## Native-app pivot — 2026-09-05

**Read this section first if you're starting a session on this project.** The client stops being
a browser/PWA and becomes a native Android app: Joakim wants per-photo handling (quality/object
detection) to run on-device *before* any server copy, plus a selective sync the user controls
that triggers **automatically in the background** with no app open — no browser API reaches a
closed OS photo library, so a PWA structurally can't do this (full reasoning:
[curation/IDENTITY_MATCHING.md](curation/IDENTITY_MATCHING.md)'s "Reversed 2026-09-05" note).
Distribution stays
sideloaded (a plain APK, no Google Play/App Store) — the standing anti-platform-control reasoning
that had this project avoiding a native app in the first place stays satisfied, not abandoned.
iOS is a "consider it, don't build it" note for now; Android only.

**What this does and doesn't change**: the long-term goal is unchanged — a fully FOSS,
complete-data-ownership system where each user runs on her own hardware but can lend spare
capacity to others on the network (Pillar 1, unchanged). What *is* downgraded to historical
reference, not committed design: every specific implementation and most specific design choices
built around a browser-based client — the old multi-user web server
([photo-server/](photo-server/README.md)), the browser GUI ([gui/](gui/README.md)), and this
file's own former "PWA-in-browser step" refinement of Pillar 2 below. Their code is archived,
not deleted, at [previous-work/](../previous-work/README.md), organized by sub-project — treat
any schema/architecture/library choice in there as something to weigh, not something already
settled; ask before carrying one forward. A concrete server-side design (the "server in some
user's home" piece the native app eventually syncs to) starts fresh when that work is scoped —
it doesn't resume from photo-server/'s old schema.

**Session-close context**: the session that made this pivot decision stopped mid-plan (scope
had changed enough to warrant a fresh session) after only researching, not yet writing native
code — that research found no `modules/pictures.py` on `master` pre-merge, no JDK/Android
SDK/Gradle on the dev machine, Docker available. The session immediately after this one did the
archiving described above and merged this branch into `master`.

**2026-09-06**: the detailed multi-slice plan that session drafted (Kotlin/Compose/Robolectric,
TDD throughout) was scrapped before any code was written — Joakim asked for a much smaller first
cut instead, to see the Android toolchain work at all before investing in that fuller structure.
See [mobile/README.md](mobile/README.md) for what actually got built.

## Current build vs. this vision

**Superseded by the native-app pivot above, 2026-09-05.** [photo-server/](photo-server/README.md) — the deliverable for a specific Sunday memorial, see its README — is a deliberately narrow, **closed** slice of Pillar 2 only: two known accounts, no data leaves the server, no network sharing. None of the other three pillars are in scope for that build.

**Reaffirmed 2026-07-27, generalized beyond just that one build**: this applies to *every* current design thread, not only photo-server specifically — [tags/](tags/README.md), [upload-and-share/](upload-and-share/README.md), all of it. The single VPS is the sole source of truth for all current work; nothing in today's design should assume or route through Pillar 1's DFS. Pillar 1 is a real, active pillar of this vision — not necessarily distant on the calendar — but it is not part of the current design phase, and no current schema/UX decision should be shaped around it prematurely. `distributed-sync/TODO.md`'s open questions (including the metadata-placement one raised this session) are legitimate to capture there for later, but nothing about them constrains work happening now.

## Pillar 1 — Distributed storage network (DFS)

Torrent-style distributed file system across users' own NAS devices; each user's files stay encrypted, and contributing spare storage/compute earns cloud storage/AI-compute credit elsewhere on the network, minus overhead. Full description already lives in [distributed-sync/README.md](distributed-sync/README.md) — not repeated here.

**Not a purely peer-to-peer end state, clarified 2026-08-07**: most actions run on each user's own hardware, but a central server persists alongside the DFS, holding global metadata and predictions about global user behavior that are **not PII** — aggregate, cross-user signal, not any individual's photos or identifying data. Gives concrete shape to Pillar 2's "learned globally across the network" line below — that global-learning component is what this central server holds. Not yet designed — see [distributed-sync/HARDWARE.md](distributed-sync/HARDWARE.md#end-goal-architecture-user-hardware-plus-a-central-server-raised-2026-08-07) for the fuller note.

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

All four pillars are open, none committed, none scheduled. Pillar 1's timeline is the "full roadmap addendum... still pending from Joakim" open question already tracked in [distributed-sync/TODO.md](distributed-sync/TODO.md). Pillars 2–4 don't have TODOs yet because nothing is being built against them. **Exception, 2026-07-26**: Pillars 1 and 3 got a real design pass — see [upload-and-share/](upload-and-share/README.md) (per-user ownership, strict/free sharing terms, event/party mode). Still not scheduled work (no TODO.md steps yet) — a design pass, not a committed build. **2026-08-05**: added the "Core differentiator" section and the "system should help the user" principle above — positioning statements, not scope changes. **2026-09-05**: added the "Native-app pivot" section above — client moves from browser/PWA to a native Android app; every previous implementation archived to `previous-work/`, not deleted; the four pillars and the core differentiator above are unaffected by this, still the goal.
