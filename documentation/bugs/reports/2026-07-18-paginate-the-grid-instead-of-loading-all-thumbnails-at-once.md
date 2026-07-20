# Paginate the grid instead of loading all thumbnails at once

Status: **candidate, not evaluated or built**.

## What

Joakim, 2026-07-18: show only the first ~70 pictures (roughly one screen) and load the next batch once the user scrolls near the end - "isn't that AJAX?" (more precisely: infinite scroll, via `IntersectionObserver` + `fetch`, same underlying idea).

## How this relates to pre-compiling thumbnails

A different lever, not a substitute - see [2026-07-17-pre-compile-thumbnails-ahead-of-time.md](2026-07-17-pre-compile-thumbnails-ahead-of-time.md):

- **Pagination** controls *how many* thumbnails get requested at once - fewer concurrent `/thumb` requests hitting the server on first load.
- **Pre-compiling** controls *how expensive* each individual `/thumb` request is - cache hit vs. on-demand generation.

Pagination alone would still show per-image latency the first time each new batch scrolls into view, if generation is still on-demand. Pre-compiling alone still sends the full request list at once, just each one resolves fast. Complementary, not either/or.

## Why not started yet

Pre-compiling was judged the higher-leverage fix for actual latency and is already the priority-one open item. This app's data already has natural chunk boundaries (`sections[].chunks[].images` in `/api/tree`'s response, matching the existing collapse/expand album UI) that a per-album (not arbitrary-70) pagination scheme could reuse directly - worth designing around that structure rather than an arbitrary batch size, if/when this gets picked up.
