# Pre-compile thumbnails ahead of time, not on-demand

Status: **shelved 2026-07-20, not being built for now**. See "Shelved" section below before reviving this.

## Background

Joakim, 2026-07-17, refined from an earlier "background/async" framing to a concrete direction: confirmed the semaphore + `Image.draft()` fixes helped (see [2026-07-17-thumbnail-oom-under-load.md](2026-07-17-thumbnail-oom-under-load.md)), but on-demand generation still means a visible wait for any never-before-viewed thumbnail - consistent per-image latency, not a growing backlog, but still a real UX cost.

## The direction

Generate every thumbnail once, ahead of any user request, so `/thumb` at browse time is *always* a cache hit (a cheap file read - current code's existing `cache_path.exists()` fast path already does this; the change is running that generation path proactively over the whole tree, not rewriting it).

## Design decisions - answered 2026-07-18, synthesized below (not yet built)

Joakim's answers to the three open questions, then a synthesis reconciling them into one concrete design - this synthesis was worked out but never actually sent back for confirmation before the session moved on to other things (a loose end closed at wrap-up, not a decision made unilaterally - **still needs Joakim's sign-off before building**):

1. **Where the job runs**: "when a new picture gets uploaded, write a class for it and call this class manually for this here [initial] run." Event-driven per-photo processing going forward, manual invocation for the one-time backlog of existing untouched photos.
2. **What handles new photos**: "I want a process happening for each photo being added. But... perhaps when the photo is taken up on screen it should be checked: has it been handled by the latest photo-routine? Log if not and run it - extremely lean, since a picture gets handled often." Check-on-view as the practical trigger (this app has no real "upload" event today - photos just appear on disk via an external sync process, so there's no upload hook to attach to without building a filesystem watcher).
3. **Resumability**: yes, confirmed.

**Synthesis**: one idempotent method, e.g. `ThumbnailProcessor.ensure_thumbnail(photo_path)`, does the lean version-check *for free* by encoding a version number into the cache path itself (e.g. `thumbcache/v1/<hash>.jpg` instead of today's `thumbcache/<hash>.jpg`) rather than tracking "processed by which version" as separate metadata. "Has this been handled by the latest routine" becomes exactly the same cheap `exists()` check the code already does today - no new I/O, satisfies the "extremely lean, called often" requirement directly. Bumping the version number (e.g. after a future algorithm change) automatically invalidates every old thumbnail with no migration step. This one method then serves all three contexts at once, with no duplicated logic: the manual backfill script (iterate the tree, call it per photo), the existing `/thumb` route's on-demand fallback (call it on a cache miss, exactly like today), and any future event-driven trigger (a filesystem watcher, if ever built) - all three just call the same idempotent, resumable-by-construction method.

Don't rush this live against a now-working production service - confirm the synthesis above with Joakim, then TDD it properly.

## Shelved, 2026-07-20

Joakim asked to revive this after re-confirming the "mitigated" latency in [2026-07-17-thumbnail-oom-under-load.md](2026-07-17-thumbnail-oom-under-load.md), with three added requirements: (1) store the cache in a directory alongside the actual photo files rather than its current separate Docker volume, (2) clean up a thumbnail when its source file is "flagged delete," (3) have a good multi-user answer ready for whenever sharing is added. Investigation before building surfaced real forks in all three:

1. **The photos mount is read-only** (`:ro`) in both `docker-compose.yml`/`docker-compose.prod.yml`. Storing the cache alongside the photos means either dropping that protection on the live library or adding a second, writable bind-mount of the same host tree at a different container path.
2. **No delete-flag feature exists anywhere in the running photo-viewer** — `documentation/photo-server/DEFERRED.md` explicitly says this browse-and-download tool deliberately has no delete/edit workflow. Requirement 2 would mean designing and building that feature from scratch, not hooking cache-cleanup into something that already exists.
3. **No per-user photo ownership model exists yet** either (`photo_owners` is schema-only, per `documentation/photo-server/DATA_DICTIONARY.md`) — requirement 3 has nothing to attach to today.

Actual disk-size math computed during this investigation, for the next time this comes up: current thumbnails are 340×340px JPEG at quality 82 (`app/main.py`), typically 15-30KB each. Even 20,000 of them is roughly 400MB — under 0.02% of the server's 2.7TB free ZFS pool space. **Disk size was not actually a blocking constraint** by these numbers; Joakim's call to shelve was made anyway, given the RAM upgrade already on order ([HARDWARE.md](../../../photo-server/HARDWARE.md)) may address the underlying on-demand-generation latency differently, without the added scope of requirements 1-3 above. Revisit once the RAM lands and the latency is re-measured — if it's still a problem, the three forks above (not the disk-size question) are what still need real decisions before building.
