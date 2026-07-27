# Tag UX flows

Interaction-level detail for tagging and sharing, on top of [TAXONOMY.md](TAXONOMY.md)'s
category model and [SCHEMA.md](SCHEMA.md)'s tables. Vision-level, discussed
2026-07-27 — not scheduled, not spec'd to the bar
[../photo-server/TODO.md](../photo-server/TODO.md) requires before a GUI step is
build-ready (see that file's own rule on what "build-ready" means). Write or request
that level of detail when a build phase actually picks this up.

## Bounding-box tagging (people, animals, objects)

On-device object detection (see [../VISION.md](../VISION.md) Pillar 2's DPFAS phase)
pre-populates bounding boxes on a photo as **subtle, concealable** tap targets — visible
enough to notice, not so prominent they dominate the photo. Tapping one opens a
contextual prompt, seeded from the detector's own generic label:

- A person box asks **"Who is this?"**, pre-filled with the detector's generic guess
  ("man", "woman"). Typing autocompletes against the user's own prior
  `entities` records — typing "da" surfaces "Dad — Pelle Svanslös" from earlier
  tagging, so a recurring person is never re-typed from scratch.
- An animal box asks for a **name**, with the detector's guess at **type** ("dog")
  offered as a confirmable/changeable default, plus a **breed** field ("Labrador").
  A follow-up step offers linking the people in its "herd" — the owner, the family —
  via relationship tags back to their person-entities.

**The UI visually distinguishes a tag pointing at a registered account from one
pointing at a local-only person record** — e.g. a distinct badge/icon — so the user
always knows, at a glance, whether "Dad" here means an actual DPFAS account or just
her own private note. Exact visual treatment not decided; the requirement is that it
must be immediately obvious, not buried in a detail view.

## Manual bounding-box tagging — the detector isn't always right or present

A detector box is the common case, not the only case: some photos won't get a usable
detection at all (no on-device pass run yet, a missed detection, a subject the
detector doesn't recognize as a distinct object), and some detections are simply
wrong or imprecise (a box drawn too tight, two people merged into one box). The user
needs a way to draw a box by hand, not just confirm ones the detector already found.

Raised 2026-07-27, alongside the mockup build that first exposed the gap (tap-only
boxes with nothing to tap). Vision-level, same bar as the rest of this file — not
build-ready:

- A manual box is created the same way any freehand rectangle-select tool works —
  drag a corner-to-corner rectangle over the region, on the photo itself. No new
  interaction paradigm versus tapping a detector box: once drawn, it opens the exact
  same contextual form (`SCHEMA.md`'s `bounding_box` column doesn't distinguish
  detector-sourced from hand-drawn — geometry is geometry either way).
- A manual box can also **replace or adjust** a detector box that's wrong (too tight,
  merged subjects, wrong region) — not just add new ones. Exact edit affordance
  (drag an existing box's edge/corner vs. delete-and-redraw) not decided.
- Detector boxes stay visually "subtle, concealable" (this file's existing rule,
  above); a manually-drawn box has no such requirement — the user placed it herself
  and already knows it's there.

## Tagging an unregistered person — invite CTA

Confirming a person-tag against a **local-only** entity (no `linked_account_user_id`
yet) surfaces a call to action: **send an invitation link**, or **share the relevant
tag/album with her directly** — since any tag is shareable
([TAXONOMY.md](TAXONOMY.md)'s "every tag is a shareable album" section), sharing
doesn't require a separate mechanism from what already exists in
[../upload-and-share/SHARING.md](../upload-and-share/SHARING.md). Declining either
option just leaves the tag as a private local record, same as today.

## Sharing a tag as an album — the blur-preview review

Before or while sharing any tag ([TAXONOMY.md](TAXONOMY.md)'s privacy section),
the owner's own view of that tag shows:

```
┌────────────────────────────────────────────┐
│  Every non-blurry picture here will be      │
│  shared. Private pictures are blurred and   │
│  stay out of the share.                     │
├────────────────────────────────────────────┤
│  [thumb] [thumb] [▓▓▓▓▓] [thumb] [▓▓▓▓▓]    │
│                    ↑ private, blurred        │
└────────────────────────────────────────────┘
```

This is a visual confirmation step, **owner-side only** — confirmed with Joakim
2026-07-27, over the alternative of also showing a recipient blurred placeholders
for photos she wasn't given access to. A recipient's view of an already-shared tag
simply never contains the excluded photos; there's no "there's more here" tease.

## Status

Vision-level design, 2026-07-27. Not scheduled — see [TODO.md](TODO.md) and
[../photo-server/TODO.md](../photo-server/TODO.md).
