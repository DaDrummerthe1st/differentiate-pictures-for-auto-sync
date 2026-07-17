# Thumbnails fail under concurrent load

Status: **mitigated, not fully fixed**. The crash is gone (mem_limit +
semaphore + `Image.draft()`, all deployed and confirmed stable — see
"Fixes applied" below). Confirmed 2026-07-17 (post-fix): each thumbnail
now takes a *consistent* amount of time to appear, showing up exactly
when it scrolls into focus (lazy-loading, pre-existing, doing its job) -
this is normal on-demand generation latency working as designed, not a
growing backlog or degradation over a session. Remaining issue is
latency/UX (a visible wait per never-before-viewed thumbnail), not
reliability. Short version lives in [../TODO.md](../TODO.md); this file
is the full chronological trail — update it as more is learned, don't
just overwrite conclusions.

## Symptom

After the P0 deploy (2026-07-17), logged in and browsing worked, but
thumbnails showed the browser's native "broken image" icon (frame, no
picture) for most images. `/original` (raw file, no processing) worked
fine for the same files.

## Investigation log

1. **Hypothesis: RAM** (Joakim's first instinct, given HARDWARE.md's
   known-tight memory). Checked `docker stats --no-stream` at rest:
   photo-viewer using 40MiB / 256MiB (15.72%) — not under pressure
   *at that moment*. Didn't rule it out, just ruled out "constantly
   pegged" as the story.
2. **Checked for silent restarts**: `docker compose ps` showed
   photo-viewer "Up 2 minutes" while every other service showed
   26-43 minutes — a restart happened. Caveat found later: this
   session ran `docker compose up -d --build` more than once (for the
   `PHOTOS_HOST_PATH` fix), which recreates the container and resets
   its uptime/logs on its own — so a short uptime alone doesn't prove a
   crash. Needed the log check below to say more.
3. **Grepped logs for the endpoint**: `docker compose logs photo-viewer
   2>&1 | grep -iE "thumb|error|traceback|exception|killed"` returned
   **zero matches**, across all 3 "Started server process" blocks in
   the log (3 container starts total). No `/thumb` request had ever
   been logged as reaching this container.
4. **Hard refresh test** (cheap, ruled out one whole class of cause):
   fixed the *first* thumbnail. Confirms the browser was at least
   partly showing stale cached failures from earlier attempts (before
   login even worked) — but didn't fix the rest, so stale cache isn't
   the whole story.
5. **Loaded more thumbnails**: subsequent ones failed, then "the page
   died" (Joakim's words) — page became unresponsive. This is the
   strongest evidence so far: a *single* thumbnail works, but load
   (multiple concurrent Pillow open+resize+save calls) causes failure
   and then unresponsiveness. Matches resource exhaustion much better
   than a per-file code bug (path encoding, corrupt file, etc. would
   likely fail the *same* files consistently, not degrade under load).
6. **Further observation, same session**: scrolled to an album lower on
   the page, clicked a thumbnail that had *not yet* shown the broken-image
   icon (i.e. not yet requested/rendered) - it broke on that first
   request too. Refines the theory: this isn't purely "many concurrent
   requests at once" - cumulative load *across* the browsing session
   (total thumbnails generated so far, not just those in flight right
   now) may be enough on its own to degrade the service. Worth checking
   memory trend over the session's lifetime, not just an instantaneous
   snapshot, next time this is investigated.
7. **Not yet done**: capturing `dmesg | grep -i oom` and `docker stats`
   *at the moment of failure* (not at rest) to get a definitive
   OOM-kill confirmation rather than inferring one. Session ended
   (Joakim had calls) before this could be captured live.

## Leading theory (unconfirmed)

Concurrent thumbnail generation (each a real Pillow decode+resize+encode,
CPU/memory-heavy by nature) exceeds available headroom on this host
(2 cores, 3.8GB total RAM, this container's own `mem_limit: 256m`) when
several requests land at once — as a browser naturally does when
rendering a grid of thumbnails. Directly relevant to POLICY.md's
resource-efficiency constraint (2026-07-17) - this is exactly the kind
of code that needs to stay lean given the eventual Pi-class hardware
target.

## Fixes applied (2026-07-17, same session)

- **`mem_limit` raised 256m -> 512m** on the photo-viewer container
  (`docker-compose.prod.yml`) - mitigation, gives Pillow's transient
  decode/resize spikes more headroom.
- **`MAX_CONCURRENT_THUMBNAILS` semaphore** (default 2) around the
  generation path in `app/main.py`'s `thumb()` - caps how many Pillow
  decode+resize+encode calls run at once. TDD'd
  (`app/tests/test_thumb_concurrency.py`).
- **`Image.draft()`** called before `exif_transpose`/`thumbnail()` -
  lets the JPEG decoder skip full-resolution decode for a small
  thumbnail, same output size/quality, less memory/CPU per call. TDD'd
  (`app/tests/test_thumb_draft.py`).

All three deployed and confirmed stable over 2+ hours with no restarts
(previously restarting every few minutes under normal browsing). The
combination stopped the crash entirely; it did not make on-demand
generation instant - see the 2026-07-17 update above.

The RAM upgrade (ordered, not installed — HARDWARE.md) was never
re-tested in isolation before these code fixes went in; not needed now
given the above resolved the crash, but worth noting it was never ruled
in or out as a contributing factor.

## Next session should start with

Not diagnosis - the crash is resolved. Go straight to designing/building
the real next step: **pre-compile thumbnails ahead of time** (see
[../TODO.md](../TODO.md)'s top-of-file priority list for the concrete
design questions already identified) so on-demand generation latency
stops being visible to the user at all.
