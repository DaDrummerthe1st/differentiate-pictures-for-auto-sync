# upload-and-share/

Design work (no code yet) for letting every user upload her own photos and share them with per-photo ownership terms — the multi-user extension [photo-server/](../photo-server/README.md) deliberately excluded from its own closed, two-account v1. Built on branch `upload-and-share`, 2026-07-26. Lays foundation for [../VISION.md](../VISION.md) Pillar 1 (distributed storage) and Pillar 3 (presentation/sharing) while this iteration itself targets **one server only** — every "reserved" schema item is a concept, not a build, so a later real second node is an addition, not a redesign.

Resolves three items [photo-server/DEFERRED.md](../photo-server/DEFERRED.md) had flagged without a design: upload function, multi-tenant photo partitioning/per-user sharing scope, and the single consolidated media root.

## Contents

| File | What's there |
| --- | --- |
| [OWNERSHIP.md](OWNERSHIP.md) | Per-photo ownership, strict vs. free terms, torrent-style piece distribution, the moderation override |
| [UPLOAD.md](UPLOAD.md) | Upload-batch naming (replacing folder-derived `catalogue`), content-addressed storage layout |
| [SHARING.md](SHARING.md) | The three share mechanisms (platform share sheet, in-app dialog, email invite), tag verification |
| [EVENTS.md](EVENTS.md) | The party/wedding/funeral event mode — QR-code auto-tagging, upload access, visibility, TV display |
| [TODO.md](TODO.md) | What's open before any of the above gets broken into TDD steps |

Visual mockup: [prototypes/upload-and-share-mockup/](../../prototypes/upload-and-share-mockup/README.md), matching the working GUI's dark theme (`app/static/`) rather than a documentation-style page — an in-memory fake database (seeded users, photos, shares) that clicks actually mutate: switch the "Viewing as" user to see a share made as one account become visible/pending for the other. Two earlier attempts the same day didn't hold up (a claude.ai Artifact, which sends content outside this project's infrastructure per [../policies/POLICY.md](../policies/POLICY.md)'s closed-by-default rule; then a static HTML/CSS/JS prototype that turned out to just re-render this same written content instead of being a real clickable prototype with fake data and state transitions) — both removed same session, see `documentation/bugs/claude-bugs/fixed/`. The written files below remain the source of truth for the design itself; the prototype is illustrative UI only, no schema/endpoints implied.

## Non-negotiables specific to this topic

Inherits everything [photo-server/](../photo-server/README.md) inherits from [../policies/POLICY.md](../policies/POLICY.md), plus the moderation-supersedes-ownership rule that file now states as a hard, project-wide constraint (added alongside this design, 2026-07-26).

## Relationship to the wider vision

This is the first real design pass against [../VISION.md](../VISION.md) Pillars 1 and 3 — see that file's Status section. Still not committed/scheduled work; only [TODO.md](TODO.md) tracks what's actually being built.

## Status

Design only, 2026-07-26. No schema migration, no endpoints, no deployment change.
