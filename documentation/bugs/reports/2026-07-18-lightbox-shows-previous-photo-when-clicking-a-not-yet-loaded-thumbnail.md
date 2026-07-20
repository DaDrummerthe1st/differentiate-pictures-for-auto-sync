# Lightbox shows previous photo when clicking a not-yet-loaded thumbnail

Status: **investigating, not fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Joakim, 2026-07-18: clicking a grid thumbnail whose own image hasn't finished loading yet opens the full-screen lightbox popup, but it shows the *previous* photo (whatever was last viewed), not the one just clicked. Confirmed (via a clarifying question) the wrong content shows in the lightbox popup itself, not in the small grid tile.

## Investigation log

1. Static read of `app/static/app.js`'s `onThumbClick` -> `openLightbox` path: `onThumbClick` reads `thumbEl.dataset.idx` directly off the clicked DOM element (set once at render time in `renderTree`, not tied to whether that element's own `<img>` has finished loading) and passes it to `openLightbox(idx)`, which synchronously sets `currentLightboxIndex = idx` and `lbImg.src = /original?p=...allImages[idx]`. No obvious async gap or stale-closure in this path on a first read.
2. Checked whether a layout-shift misclick (grid reflowing as thumbnails lazy-load, causing a click to land on the wrong DOM element) could explain it: ruled out - `app/static/style.css`'s `.thumb` has `aspect-ratio: 1 / 1` explicitly set, so grid cells are reserved at fixed size before their image loads; no reflow to cause a misclick.
3. Checked whether `allImages`/`renderTree` could be rebuilding mid-session (which would desync a previously-read `idx`): `loadTree()` (which calls `renderTree`) is only ever called once, from `enterGallery()` at page load - no other caller found, so this shouldn't be re-running during normal browsing.
4. No root cause identified yet from static reading alone.
5. **Symptom changed after today's redeploy** (Joakim, 2026-07-18, post `d147c04` deploy): clicking a not-yet-loaded thumbnail now shows *nothing at all* - not even the broken-image placeholder icon a failed `<img>` load normally shows. Previously it showed the *previous* photo instead. Not yet understood whether this is the same underlying bug presenting differently (e.g. now correctly failing to load the wrong content, where it previously somehow rendered stale content), or a distinct regression introduced by one of today's other changes (the `docs_url=None` fix, the schema-init lifespan handler, or something else entirely unrelated). Needs a fresh live repro - don't assume continuity with the earlier "previous photo" symptom.

## Leading theory (unconfirmed)

None confirmed. Candidate to explore next: whether rapid close-lightbox-then-click-next-thumbnail while the previous photo's `/original` fetch is still in flight somehow leaves stale state - though standard `<img>` behavior discards a late-arriving response for an element once its `src` has since changed, so this would need to be demonstrated, not assumed.

## Next session should start with

Needs a live repro, not more static reading: reproduce with browser DevTools open (Network + Console tabs), on a still-slow connection or throttled network to make the timing window wide enough to catch reliably. Capture: which two photos were involved, whether it's consistent or intermittent, and what the Network tab shows for the `/original` requests around the click (was a request for the "wrong" photo actually still pending, or did it complete with content for a different `p=` value than its own URL - the latter would point at a server-side bug instead of a client-side one, and would be a much more serious finding).
