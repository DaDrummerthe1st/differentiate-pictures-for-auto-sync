# Unauthenticated static UI shell loads before any login check

Status: **fixed 2026-07-23**. See "Resolution" below.

## Symptom

Found 2026-07-17, live during the P0 human checkpoint: visiting `https://photos.reuterborg.se/` shows the photo-viewer's "choose where to download photos" onboarding prompt first, regardless of session state — confusing for a non-technical user expecting a login screen.

Not a security bug: no photo data is in that prompt, and the actual data endpoints are correctly gated (confirmed via the 401 tests). It's a UX rough edge.

## Root cause

`app/main.py` mounts `StaticFiles` at `/` ungated by design (today's P0 only gated the API routes, not the shell), so `index.html`/`app.js` always load first; only the first data fetch (`/api/tree` etc.) discovers there's no session and redirects to `/login` via `app.js`'s `authFetch`.

## Extended 2026-07-17

This prompt reappears on *every* page refresh, even when already logged in and even after previously dismissing it — not just on first visit. Worse in Firefox specifically: Firefox doesn't support the File System Access API the folder-picker needs, so the prompt is pure friction there (the app's own text admits it - "den här webbläsaren stöder inte mappval... men du kan fortsätta ändå").

## Resolution (2026-07-23)

Revisited with three open product questions. Two turned out to already be resolved by unrelated prior work (the "Download-folder UX rework" — see `documentation/gui/TODO.md`), which had moved the folder-picker off the blocking upfront-onboarding design this file originally described:

- **One-time choice, persisted?** Already resolved: `app/static/app.js`'s `maybeOfferFolderPicker()` (added by the folder-UX rework) offers the picker once, lazily, on the first actual download action — not upfront — and remembers "done" via `localStorage` so it never re-prompts. Persistence is client-side (`localStorage`), not server-side as originally floated, but functionally the "reappears every refresh" complaint no longer applies.
- **Unsupported browsers (no File System Access API)?** Already resolved: `maybeOfferFolderPicker()` returns early when `window.showDirectoryPicker` isn't a function — no prompt shown at all. The old "your browser can't do this, but continue anyway" message no longer exists anywhere in `app.js`.
- **Pre-render session check?** This was the file's actual remaining bug and got a real fix: added a server-side gate. `app/main.py` now has an explicit `@app.get("/")` route (registered before the `StaticFiles` mount) that checks the access-token cookie via `app/auth.py`'s new `has_valid_session()` and redirects to `/login` before ever serving `index.html`, instead of relying on the client-side `authFetch` 401-then-redirect that only fired after the shell had already rendered. `/app.js`/`/style.css` stay ungated via the existing `StaticFiles` mount, unchanged. Covered by 5 new tests in `app/tests/test_auth_gate.py` (`test_root_*`): missing cookie, garbage cookie, expired token, wrong token type all redirect to `/login`; a valid access token serves the shell.
