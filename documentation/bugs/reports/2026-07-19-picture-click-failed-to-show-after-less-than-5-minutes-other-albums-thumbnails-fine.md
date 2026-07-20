# Picture click failed to show after less than 5 minutes, other albums thumbnails fine

Status: **investigating, not fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Joakim clicked a picture in the live GUI (`photos.reuterborg.se`) after waiting less than 5 minutes (under the access-token's own expiry, and comfortably under the new proactive silent-refresh's 4-minute interval shipped earlier this same session) - it "couldn't be shown". Separately confirmed: after this, thumbnails in a *different* album loaded fine, ruling out a session-wide 401 (the cookie was still valid at that point). Exact status code / error not yet captured - asked Joakim to check DevTools Network tab for the specific failed request, answer not in yet.

## Investigation log

1. Re-read this session's own DOM-unload + lightbox-index refactor (`app.js`'s `renderTree()`/`renderActiveAlbum()`/`sectionImageOffset`/ `openLightbox()`/`lightboxStep()`) for an off-by-one or stale-index bug, since that's new code from earlier today. On inspection, the index math looks internally consistent: `allImages`/ `sectionImageOffset` are computed once per `renderTree()` call across *all* sections (not just the active one), and `renderActiveAlbum()` assigns `dataset.idx` starting from the correct per-section offset. No bug found by reading alone - not the same as confirmed absent.
2. Confirmed the lightbox's full-size image (`lbImg.src = /original?p=...`) is a plain `<img>` load, same as grid thumbnails - bypasses `authFetch`'s reactive refresh entirely, same mechanism as the already-fixed thumbnail-401 bug. But the "other album's thumbnails loaded fine right after" data point argues against a plain expired-token explanation for *this* specific failure, since that would have broken those too.
3. Two live candidates, neither confirmed: (a) a real 404/500 specific to that one file (e.g. a path-encoding edge case with the Swedish filename's non-ASCII characters, or a corrupt/mismatched-extension file caught by `_sniff_file_type`), or (b) the *separate*, already-documented, pre-existing bug (`2026-07-18-lightbox-shows-previous-photo-when-clicking-a-not-yet-loaded-thumbnail.md`)
   - though that one's recorded symptom is "shows previous/no photo," not necessarily "broken image icon," so may not be the same thing.

## Leading theory (unconfirmed)

Not a session/auth problem (ruled out by the other album's thumbnails working). Most likely either a real per-file serving bug or the pre-existing not-yet-loaded-thumbnail race - can't distinguish without the actual status code.

## Next session should start with

Get the exact status code/error for the specific failed request from DevTools Network tab (or a fresh repro with Network tab already open) - everything above is inference from one data point, not confirmed. If it turns out to be a 404, get the exact file path requested and check it directly against the real filesystem for an encoding/existence mismatch.
