# Upload reports finished but no files land in folder or appear in browser

Status: **investigating, not fixed - no live repro yet, reported at session end**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Joakim, 2026-08-13, testing the just-deployed upload-progress-banner fix (see `2026-08-13-photo-upload-has-no-visible-progress-and-uploaded-photos-aren-t-shown.md`) live on the real server: the upload appeared to finish (progress banner completed), no persistent/visible error was shown, but afterward no files exist in `dpfas_media/<username>/` on disk and nothing new appears in the browser. Not yet confirmed whether the client-side "X/Y misslyckades" `alert()` fired and was just missed/dismissed (it's a one-shot modal, nothing persists afterward either way), or whether the server actually returned 2xx for files it didn't persist.

## Investigation log

1. **Not live-reproduced this session** - reported right at session close, no time to check the real DevTools Network tab or server logs before wrapping up. Everything below is a static-code-reading hypothesis list only, ranked by plausibility, not a confirmed cause.
2. **Leading candidate: `PICTURE_EXTS` may reject the actual files Joakim tried to upload.** `/api/upload` (`app/main.py:607-627`) 400s on any extension not in `PICTURE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp"}` (`app/main.py:52`) - notably **no `.heic`/`.heif`** (the default format for recent iPhone photos) and no video extensions, even though the app's own *browsing* side (`MEDIA_EXTS`/`_EXPECTED_LABEL_FOR_EXT`) clearly treats `.heic` and video as legitimate media elsewhere. If Joakim's upload source was a phone exporting HEIC (or any non-`PICTURE_EXTS` format), every file in the batch would 400, `res.ok` would be false for all of them, `uploaded` would stay 0, and the *existing* code path (before today's fixes and also after) shows exactly one client-side `alert()` with the failure count - easy to miss/dismiss and, per this report, apparently was.
3. **Second candidate: `MAX_PHOTO_UPLOAD_BYTES` (25MB default, `app/main.py:33`)** - same effect (400, silently-dismissable alert) if source files (e.g. real camera/phone originals, not pre-resized) exceed that cap.
4. **Not yet ruled out**: a genuine server-side bug where `/api/upload` returns 2xx without actually persisting (e.g. an exception after the response is prepared but the client still reads `ok`) - would require actual server logs or a live repro to confirm or rule out, can't be resolved by reading the route function alone (`app/main.py:607-627` reads as straightforwardly synchronous and correct: read bytes -> hash -> write -> return, no obvious swallowed-exception path).
5. **Confirmed unrelated to this session's uncommitted UI work**: this bug was reported against the *already-deployed* banner/jump-to-album fix, before any of the new byte-progress/speed/file-list changes below were tested live. Those changes are irrelevant to whether files actually land on disk - they only change how progress is displayed client-side.

## Leading theory (unconfirmed)

Files Joakim tried to upload are being rejected by `/api/upload`'s extension allowlist (`PICTURE_EXTS`, likely missing HEIC) or size cap, the request returns 400, and the *existing* failure feedback (a single dismissable `alert()`, no persistent record anywhere in the UI) is easy enough to miss that it reads as "no error at all."

## Next session should start with

1. Live repro with DevTools Network tab open: pick the exact files Joakim was actually trying to upload, watch `/api/upload`'s real response status/body per file.
2. If it's a 400 from `PICTURE_EXTS`/`MAX_PHOTO_UPLOAD_BYTES`: decide with Joakim whether to widen `PICTURE_EXTS` to match what the browsing side already accepts (at minimum `.heic`), and/or whether the failure needs a more persistent UI treatment than a one-shot `alert()` (the per-file list added in this session's uncommitted work - see below - already shows "misslyckades" per row and stays visible until the next upload, which would incidentally help here once verified and shipped).
3. If it's a 2xx-but-nothing-written case: needs server log inspection on the real host, not just static reading.

## Uncommitted work in progress at session end, 2026-08-13

Joakim asked (after confirming the progress banner itself was visible and working) for byte-level speed/data-transferred stats and a collapsible per-file list. Implemented but **not yet verified live, not committed**:
- `app/static/app.js`: new `xhrUpload`/`authXhrUpload` (switches upload transport from `fetch` to `XMLHttpRequest` for real upload-progress events; mirrors `authFetch`'s silent-refresh-then-retry-once behavior via the same shared `_refreshInFlight`), `formatBytes()`, a rolling 3-second speed sample window, and a per-file list (`#uploadFileList`, toggled by `#uploadFileListToggle`) showing each file's name/size/status (väntar/laddar upp/klar/misslyckades).
- `app/static/index.html` / `style.css`: new `#uploadBannerStats`, `#uploadFileListToggle`, `#uploadFileList` markup and styling.
- **Deliberately left uncommitted**: verifying this needs real successful uploads to watch progress/speed/list update correctly, and per the bug above, uploads may not currently be succeeding at all against the real library depending on what's causing this bug - testing this UI and fixing the upload-failure bug should probably happen together next session, in whichever order makes sense once the failure's actual cause is known live.
