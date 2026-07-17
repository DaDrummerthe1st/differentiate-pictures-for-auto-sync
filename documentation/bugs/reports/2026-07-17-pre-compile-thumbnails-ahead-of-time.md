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

## Real design decisions needed before building (not to be guessed at live)

1. **Where the job runs** - in-process at startup (mustn't block
   uvicorn actually serving requests), a separate one-off script, or a
   scheduled job.
2. **What handles photos added after the initial pass** - a periodic
   re-scan, or keep today's on-demand path as a fallback for
   cache-misses so pre-compiling isn't all-or-nothing.
3. **Whether it needs to be resumable** if interrupted mid-batch (a
   restart, a crash) rather than starting over.

Don't rush this live against a now-working production service - design
and TDD it properly next session.
