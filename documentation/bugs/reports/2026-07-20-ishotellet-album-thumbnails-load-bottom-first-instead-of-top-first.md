# Ishotellet album thumbnails load bottom-first instead of top-first

Status: **investigating, not fixed**. Keep this file as the full
chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Joakim, 2026-07-20, browsing the "Ishotellet" album on `photos.reuterborg.se` live (while re-testing the separate thumbnail-OOM bug, see [2026-07-17-thumbnail-oom-under-load.md](2026-07-17-thumbnail-oom-under-load.md)): thumbnails visibly appeared bottom-of-page first, before the ones higher up had loaded. He noticed the top of the album still empty/unloaded and had to scroll down to see the bottom already populated. Confirmed via a clarifying question that this specifically means thumbnails rendering bottom-first, not the page auto-scrolling to the bottom. Album has "lots of files" - exact count not yet captured.

## Investigation log

Not yet investigated live - this was flagged in passing during an unrelated bug test, not chased down in the moment.

## Leading theory (unconfirmed)

`app/static/app.js`'s thumbnail `<img>` tags use native `loading="lazy"` (see `renderActiveAlbum()`), which lets the browser decide its own priority/order for images outside the initial viewport - normally this loads top-to-bottom as the user scrolls, so bottom-first is unexpected. Two unconfirmed candidates: (1) something about how a large album's chunks are appended to the DOM causes the browser's lazy-load heuristic to misjudge which images are "near" the viewport first, or (2) a large enough album makes an early layout shift (chunk-title/grid elements sized before their images load) put the browser's initial guess of "visible" thumbnails somewhere other than the true top. Neither checked against real DOM/Network evidence yet.

## Next session should start with

A live repro with DevTools open (Network tab, sorted by request order) on this specific album (or another large one) - capture the actual order `/thumb` requests fire in, and whether it correlates with scroll position, chunk boundaries, or something else. Get the real file count for Ishotellet first (see the `find`/`du` command shared with Joakim in chat) to know if this only shows up past some size threshold.
