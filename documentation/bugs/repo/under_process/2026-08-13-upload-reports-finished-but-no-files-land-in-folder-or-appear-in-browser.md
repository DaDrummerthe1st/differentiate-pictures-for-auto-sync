# Upload reports finished but no files land in folder or appear in browser

Status: **root-caused via live repro, fix not yet deployed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

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

## Live repro, 2026-08-13 (session 2)

Joakim confirmed the source files were plain JPEG (not HEIC) - ruling out the `PICTURE_EXTS` theory in the "Leading theory" section above before it was even tested. He then reproduced live with DevTools Network tab open:

- `POST /api/upload` -> **401**, response body `{"detail": "Invalid or expired session"}`.
- Request `Content-Length` was ~1.6MB - nowhere near the 25MB `MAX_PHOTO_UPLOAD_BYTES` cap, ruling out the size-cap theory too.
- Decoding the `photo_server_access` cookie sent with that exact request: `{"sub": "2", "role": "admin", "type": "access", "iat": ..., "exp": ..., "jti": ...}` - **no `username` claim at all** (not `null` - the key is entirely absent). `exp` was ~3.5 minutes in the future at request time, so this was not ordinary token expiry.

### Root cause (confirmed by code + git history, not yet confirmed against the live container image)

`app/auth.py`'s `require_session_with_username` (used by `/api/upload` and nothing else that Joakim hit in this repro) explicitly 401s with this exact message when the decoded payload has no `username` key (`app/auth.py:72-74`). A payload missing the key entirely - not `null` - is only possible if the token was minted by code *older than* commit `66f37ad` ("Add opaque username column, CLI auto-generation, and JWT claim"), which is what first added `"username": username` to `create_access_token` in `server/app/tokens.py:58`. A `NULL` username column value would still serialize as `"username": null`, not omit the key - so this isn't a data problem, it's a **stale `auth` container image**.

`66f37ad` and `3fdf580` (which added `/api/upload` itself) are both already well back in this branch's history relative to `220b3f2` (the commit Joakim was testing when he first hit this bug) - so the source has had the fix in it for a while. The likely explanation: some deploy in between only rebuilt `photo-viewer` (this session's own task brief did exactly that - "static files bake into the photo-viewer image, so ... `--build photo-viewer`") without also rebuilding `auth`, even though `server/app/tokens.py` changed too. `documentation/photo-server/DEPLOYMENT.md`'s general deploy command (line 39) rebuilds every service with no filter, so this only bites when someone (reasonably) uses a narrower, service-scoped rebuild because only the photo-viewer side looked like it needed one.

Every other endpoint Joakim uses day to day goes through plain `require_session` (no username needed), which is why browsing/everything-else kept working fine while uploads specifically 401ed - easy to read as "uploads are broken" rather than "the whole deploy is half-stale," which is what actually explains the silent all-files-fail pattern (this 401 happens in a FastAPI dependency, before `PICTURE_EXTS`/size checks or any file writing ever runs).

### Next step (not run by this session - deployment is always Joakim's own hand, POLICY.md)

Rebuild and redeploy the `auth` service specifically (or run the unfiltered `docker compose -f docker-compose.prod.yml up -d --build` from DEPLOYMENT.md, which rebuilds everything and sidesteps this whole class of skew):

```
git pull
docker compose -f docker-compose.prod.yml up -d --build auth
```

Then retry the same upload and re-check the `/api/upload` response and the decoded access-token payload the same way, to confirm `username` is present and the upload actually lands in `dpfas_media/<username>/`.

### Rebuilding auth surfaced a second, more severe issue (still 2026-08-13)

Joakim ran the rebuild above. `auth` came up already primed for the real fix (it now embeds `username`), but immediately crash-looped on a *different* error: `ensure_schema()`'s `ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT UNIQUE NOT NULL` raised `psycopg.errors.NotNullViolation` - prod's `users` table already had 2 rows (Joakim/admin, Elisabeth/member) predating the column, and Postgres can't add a `NOT NULL` column with no default against non-empty rows. This took `auth` (hence login/refresh/whoami, not just uploads) fully down, confirming the "stale image" theory above was right - this migration had simply never run against prod before.

This session's first proposed fix - copy `documentation/photo-server/DEPLOYMENT.md`'s already-written `DELETE FROM audit_log; DELETE FROM users;` and recreate both accounts - was wrong to hand over uncritically; see [documentation/bugs/claude-bugs/fixed/2026-08-13-recommended-raw-destructive-sql-against-production-instead-of-a-controlled-script.md](../../claude-bugs/fixed/2026-08-13-recommended-raw-destructive-sql-against-production-instead-of-a-controlled-script.md). Built instead: `server/app/db.py`'s `backfill_missing_usernames()` (assigns an opaque username to any row missing one, in place, non-destructively) plus `server/scripts/backfill_username.py`, a one-off CLI entry point that runs from the `auth` image without going through the crashing `uvicorn` startup path. `DEPLOYMENT.md` §4 now documents this as the real one-time step:

```
docker compose -f docker-compose.prod.yml run --rm auth python -m scripts.backfill_username
docker compose -f docker-compose.prod.yml up -d
```

Not yet run against prod - Joakim still needs to run this, then retry the upload and confirm `username` is now present in the token and the file actually lands in `dpfas_media/<username>/`.

## Uncommitted work in progress at session end, 2026-08-13

Joakim asked (after confirming the progress banner itself was visible and working) for byte-level speed/data-transferred stats and a collapsible per-file list. Implemented but **not yet verified live, not committed**:
- `app/static/app.js`: new `xhrUpload`/`authXhrUpload` (switches upload transport from `fetch` to `XMLHttpRequest` for real upload-progress events; mirrors `authFetch`'s silent-refresh-then-retry-once behavior via the same shared `_refreshInFlight`), `formatBytes()`, a rolling 3-second speed sample window, and a per-file list (`#uploadFileList`, toggled by `#uploadFileListToggle`) showing each file's name/size/status (väntar/laddar upp/klar/misslyckades).
- `app/static/index.html` / `style.css`: new `#uploadBannerStats`, `#uploadFileListToggle`, `#uploadFileList` markup and styling.
- **Deliberately left uncommitted**: verifying this needs real successful uploads to watch progress/speed/list update correctly, and per the bug above, uploads may not currently be succeeding at all against the real library depending on what's causing this bug - testing this UI and fixing the upload-failure bug should probably happen together next session, in whichever order makes sense once the failure's actual cause is known live.
