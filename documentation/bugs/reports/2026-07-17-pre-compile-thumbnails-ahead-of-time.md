# Pre-compile thumbnails ahead of time, not on-demand

Status: **designed direction agreed, not built - highest priority open item**.

## Background

Joakim, 2026-07-17, refined from an earlier "background/async" framing
to a concrete direction: confirmed the semaphore + `Image.draft()`
fixes helped (see
[2026-07-17-thumbnail-oom-under-load.md](2026-07-17-thumbnail-oom-under-load.md)),
but on-demand generation still means a visible wait for any
never-before-viewed thumbnail - consistent per-image latency, not a
growing backlog, but still a real UX cost.

## The direction

Generate every thumbnail once, ahead of any user request, so `/thumb`
at browse time is *always* a cache hit (a cheap file read - current
code's existing `cache_path.exists()` fast path already does this; the
change is running that generation path proactively over the whole tree,
not rewriting it).

## Design decisions - answered 2026-07-18, synthesized below (not yet built)

Joakim's answers to the three open questions, then a synthesis
reconciling them into one concrete design - this synthesis was worked
out but never actually sent back for confirmation before the session
moved on to other things (a loose end closed at wrap-up, not a decision
made unilaterally - **still needs Joakim's sign-off before building**):

1. **Where the job runs**: "when a new picture gets uploaded, write a
   class for it and call this class manually for this here [initial]
   run." Event-driven per-photo processing going forward, manual
   invocation for the one-time backlog of existing untouched photos.
2. **What handles new photos**: "I want a process happening for each
   photo being added. But... perhaps when the photo is taken up on
   screen it should be checked: has it been handled by the latest
   photo-routine? Log if not and run it - extremely lean, since a
   picture gets handled often." Check-on-view as the practical trigger
   (this app has no real "upload" event today - photos just appear on
   disk via an external sync process, so there's no upload hook to
   attach to without building a filesystem watcher).
3. **Resumability**: yes, confirmed.

**Synthesis**: one idempotent method, e.g.
`ThumbnailProcessor.ensure_thumbnail(photo_path)`, does the lean
version-check *for free* by encoding a version number into the cache
path itself (e.g. `thumbcache/v1/<hash>.jpg` instead of today's
`thumbcache/<hash>.jpg`) rather than tracking "processed by which
version" as separate metadata. "Has this been handled by the latest
routine" becomes exactly the same cheap `exists()` check the code
already does today - no new I/O, satisfies the "extremely lean, called
often" requirement directly. Bumping the version number (e.g. after a
future algorithm change) automatically invalidates every old thumbnail
with no migration step. This one method then serves all three contexts
at once, with no duplicated logic: the manual backfill script (iterate
the tree, call it per photo), the existing `/thumb` route's on-demand
fallback (call it on a cache miss, exactly like today), and any future
event-driven trigger (a filesystem watcher, if ever built) - all three
just call the same idempotent, resumable-by-construction method.

Don't rush this live against a now-working production service -
confirm the synthesis above with Joakim, then TDD it properly.
