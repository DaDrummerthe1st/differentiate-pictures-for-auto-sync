# Photo upload has no visible progress and uploaded photos aren't shown

Status: **fix implemented 2026-08-13, pending live verification on the real server**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Joakim, 2026-08-13: after choosing photos to upload, nothing on screen indicates upload progress, and the uploaded photos never appear as thumbnails.

## Investigation log (static code reading, both root causes confirmed without needing a live repro)

1. **No visible progress, confirmed**: the upload `<input>`'s `change` handler (`app/static/app.js`, was around line 1053) wrote progress text into `uploadBtn.textContent` (`Laddar upp (n/total)...`) during the loop. But `uploadBtn` lives inside `#moreActionsMenu` (`index.html`), and the button's own `click` handler hides that whole menu (`classList.add("hidden")`) *before* the file picker even opens - so for the entire duration of the upload, the element being updated is `display: none`. The progress text existed in code but was never visible.
2. **Uploaded photos not shown, confirmed**: `/api/upload` (`app/main.py:607-627`) writes each uploaded file flat into `dpfas_media/<username>/<sha256>.<ext>` - no subfolder. `/api/tree` (`app/main.py:352-391`), which builds the album list the frontend renders, groups a file with no parent directory (`rel.parent.parts` is empty) under the literal headline/chunk `"."` - confirmed via Python's `Path('.').parts == ()`. Meanwhile `renderTree()` (`app.js`) only changes the frontend's `activeHeadline` (which album is actually displayed) when the *previously* active headline no longer exists in the new tree (line ~443: `if (!sections.some(s => s.headline === activeHeadline))`). If the user was already viewing some other album (e.g. the family library) when they uploaded, that album still exists after the upload, so the view never switches to `"."` - the newly uploaded photo is sitting in the tree data the frontend fetched, just never rendered, because the visible album never changed. The upload itself succeeded (`loadTree()` was already being called after the loop) - nothing was silently failing server-side.

## Fix implemented, 2026-08-13

`app/static/index.html` / `style.css`: new `#uploadBanner`, a fixed top banner (same pattern as the existing `#recordingBanner`) with a real progress bar (`#uploadProgressTrack`/`#uploadProgressFill`) - visible regardless of `#moreActionsMenu`'s state, unlike the old button-text approach.

`app/static/app.js`:
- The upload `change` handler now writes progress into the banner (text + bar fill, tracking every processed file including failures, not just successes, so the bar reliably reaches 100% by the time the loop ends).
- After a successful upload and `loadTree()`, explicitly calls the existing `setActiveAlbum(UPLOADS_HEADLINE)` (`UPLOADS_HEADLINE = "."`, matching `api_tree`'s grouping) so the view actually jumps to show the just-uploaded photos, instead of leaving the user on whatever album they'd been browsing.
- Added `headlineLabel()` so the literal `"."` headline displays as "Uppladdade bilder" (both in the album-switcher pills and the album's own `<h2>`) rather than a bare dot, which would otherwise be a confusing thing to show a non-technical user (Elisabeth/her mother) right after they upload something.

Not yet verified against the real deployed app - same `--build` deployment requirement as the lightbox fix (static files baked into the `photo-viewer` image).

## Next session should start with

If Joakim confirms this fixes what he sees live (progress bar visible during upload, uploaded photos appear immediately under "Uppladdade bilder"), move this file to `../fixed/` with a `-SOLVED` suffix. If uploaded photos still don't appear even after landing in the right album, that would mean `/api/tree`'s content-sniff check (`app/main.py:361-369`, comparing file extension against magic-byte-detected type) is rejecting them - worth checking the browser's actual uploaded file types against that list next, not assumed innocent just because this fix addresses the two reported symptoms.
