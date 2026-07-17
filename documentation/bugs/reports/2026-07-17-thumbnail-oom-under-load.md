# Thumbnails fail under concurrent load

Status: **investigating, not fixed**. Short version lives in
[../TODO.md](../TODO.md); this file is the full chronological trail —
update it as more is learned, don't just overwrite conclusions.

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
6. **Not yet done**: capturing `dmesg | grep -i oom` and `docker stats`
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

## Candidate fixes (not evaluated yet - needs real profiling first)

- Cap concurrent thumbnail generation server-side (a semaphore/queue),
  so load degrades gracefully (slower) instead of failing outright.
- Pre-generate/warm the thumbnail cache instead of generating on first
  view (shifts cost to a background job instead of the request path).
- Lower per-thumbnail memory footprint (e.g. `Image.draft()` before
  resize, to avoid decoding a full-resolution image just to shrink it).
- The already-known RAM upgrade (ordered, not installed — HARDWARE.md)
  may simply resolve this once fitted; worth re-testing before assuming
  a code change is required at all.

## Next session should start with

`dmesg | grep -i oom` and a `docker stats` capture *during* a deliberate
attempt to load many thumbnails at once, to confirm or rule out the OOM
theory before spending time on any of the candidate fixes above.
