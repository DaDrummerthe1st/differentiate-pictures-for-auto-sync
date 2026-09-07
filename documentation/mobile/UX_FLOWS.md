# mobile/ UX flows

Interaction-level UX detail for the native Android app, split out as its own file 2026-09-07 at
Joakim's explicit request — UX design rules get their own documentation dimension, not folded into
[README.md](README.md)'s architecture/status notes or [TODO.md](TODO.md)'s backlog. Same bar as
[../tags/UX_FLOWS.md](../tags/UX_FLOWS.md): vision-level, discussed and reasoned through, not
build-ready spec — write that level of detail when a build phase actually picks an item up.

## Swipe-to-triage gesture — design discussion, 2026-09-07, not built

Raised alongside the app's storage-transparency goal (see README.md/VISION.md): an easy swipe
gesture to quickly declutter a photo library, while satisfying a **hard, non-negotiable rule**
Joakim stated explicitly: the user must always be able to recover from a wrong swipe, even after
any immediate undo-timeout has passed, and even after several further actions happened in between
the wrongful one and the latest.

### What the two swipe directions actually mean — proposed, needs confirmation

Joakim's own framing groups the four named actions into two pairs by *intent*, not necessarily two
separate gestures each: "delete/archive" (one direction) vs. "tag/set-to-album" (the other). Read
literally that's ambiguous — is "delete" vs. "archive" a third choice needed per swipe, or are they
close enough in intent to collapse into one gesture? **Proposed reading, not yet confirmed**:
collapse them into a genuine two-way choice, since it's simpler to learn (matters for the explicit
"aim for computer illiterates" bar) and both named actions on each side share the same underlying
intent:

- **One direction — "get this out of my main view"**: covers both "delete" and "archive" as the
  *same* user-facing action — the photo leaves the main grid into one recoverable holding area
  (name TBD — "Removed", reusing "Archive," or something else). No separate gesture needed to pick
  between "delete" and "archive" specifically; that distinction only matters later, at the point of
  actually reclaiming storage (see below), which is a separate, deliberate action, not part of the
  swipe.
- **Other direction — "I want to organize/keep this"**: opens a tag/album picker. Trivially
  reversible on its own (removing a tag or moving out of an album is just as easy at any later
  time) — the hard undo rule below has no real teeth here, only on the "remove" side.

**Which physical direction (left/right) maps to which meaning is a real open question, not a
solved industry standard** — researched 2026-09-07: Tinder's right-swipe-is-positive convention is
probably the single most widely learned swipe association today (right = keep/yes, left =
reject/no), which argues for **right = organize/keep, left = remove**. Email apps (Gmail-style
swipe-to-archive/delete) don't offer a consistent counter-precedent — that mapping is commonly
user-configurable rather than fixed, so it isn't a competing "standard" so much as evidence there
isn't one. **Confirmed with Joakim 2026-09-07**: right = organize/keep, left = remove, matching Tinder's more
universally learned pattern.

**Up/down, raised as a maybe**: no gesture is assigned yet. Given the two-way collapse above
already covers both named use cases, up/down isn't load-bearing for the core interaction — proposed
to defer it until the left/right interaction is actually on Joakim's phone and confirmed to feel
right, rather than design a third axis speculatively. Candidate future use once revisited: separating
"archive" from "delete" as distinct swipe targets after all, if the collapsed version turns out to
feel wrong in practice.

### The hard recoverability rule — two-tier model, grounded in real precedent

Researched 2026-09-07 (Apple Support, Google Photos Help) for how established photo apps already
solve exactly this tension (fast, low-friction removal vs. real recoverability):

- **Apple Photos' "Recently Deleted" album**: flat 30-day retention — a deleted photo/video stays
  recoverable for 30 days, still counts against storage during that window, then is permanently
  removed. [Source](https://support.apple.com/en-us/124460).
- **Google Photos' trash**: 60 days for backed-up content, 30 days for content that was never
  backed up. [Source](https://support.google.com/photos/answer/9343482).

Both use the same shape: an immediate, cheap "undo the thing I just did" affordance, **plus** a
longer, durable holding period that doesn't depend on how many actions happened since. **Proposed
design for this app, adapting that shape**:

1. **Tier 1 — immediate undo**: a short-lived toast/snackbar with an "Undo" action right after
   every swipe (Android's own standard Material pattern for reversible actions), a few seconds
   long. Catches the "oops, wrong direction, right now" case cheaply.
2. **Tier 2 — a durable "Removed" holding area**: every "removed" photo lands here regardless of
   Tier 1, browsable and individually or bulk-restorable, satisfying the actual hard rule (recovery
   survives both the undo-timeout and any number of actions in between).
3. **Real deletion (freeing on-device storage) is a separate, deliberate action, never automatic
   by default** — proposed stricter than both Apple's and Google's precedent (which both
   auto-purge after their fixed window) specifically because Joakim's rule is stated as
   non-negotiable, not "recoverable for a while." The "Removed" bin's total reclaimable size feeds
   directly into the storage-transparency dashboard (`TODO.md`'s backlog item) — "empty this to
   free 2.3GB" becomes a visible, explicit choice the user makes, not a timer running quietly in
   the background. **Confirmed with Joakim 2026-09-07**: manual-only by default (no timer runs
   unless the user turns one on), with an *optional* user-configured auto-purge timer (e.g.
   modeled on Apple's 30-day default) available for anyone who'd rather not manage it by hand —
   exact settings-UI treatment not designed here, just the default/opt-in split.

### Status

Opened 2026-09-07. Both open questions confirmed with Joakim same day: right=keep/left=remove
direction mapping, and manual-only-by-default purge with an opt-in timer. Nothing built yet — next
step is translating this into an actual build slice (gesture detection, the Removed-bin schema on
top of the Room table already decided in [TODO.md](TODO.md), the undo snackbar).

## Bounding boxes in the grid view — don't draw them there

Raised 2026-09-07: once on-device object detection exists, how should the grid (a "contact sheet,"
[GLOSSARY.md](../GLOSSARY.md)) show that a photo has detections? **Researched real precedent**:
neither Google Photos nor Apple Photos draws box outlines over grid thumbnails — Apple's People &
Pets and Google's face-grouping both use a *separate* browsing view (cropped face thumbnails, a
dedicated collection), and Google's "Photo Stacks" grouping uses a small badge icon on the grid
tile, never a drawn box.

**Proposed, matching that precedent and this project's own existing design**: don't draw boxes in
the grid at all — a thumbnail is too small for an outline to read as anything but clutter, and
[../tags/UX_FLOWS.md](../tags/UX_FLOWS.md) already designed box-level interaction (tap a box, confirm/
name it) for the **fullscreen** per-photo view, which is the right screen for that level of detail
anyway. The grid's own job (fast visual scanning, per the contact-sheet's whole point) is better
served by a small, subtle **corner badge** — e.g. a face/object-count icon — signaling "this photo
has detections to review" without drawing over the image itself. Exact badge design (icon set,
placement, whether it distinguishes people vs. objects) not decided — flagged for whenever
on-device detection is actually being built, not before.

### Status

Opened 2026-09-07, not built. Depends on on-device object detection existing at all
([TODO.md](TODO.md)'s NanoDet-Plus porting item).
