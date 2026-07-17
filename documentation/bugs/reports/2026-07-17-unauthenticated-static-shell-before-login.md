# Unauthenticated static UI shell loads before any login check

Status: **root cause understood, real fix needs product input**.

## Symptom

Found 2026-07-17, live during the P0 human checkpoint: visiting
`https://photos.reuterborg.se/` shows the photo-viewer's "choose where
to download photos" onboarding prompt first, regardless of session
state — confusing for a non-technical user expecting a login screen.

Not a security bug: no photo data is in that prompt, and the actual
data endpoints are correctly gated (confirmed via the 401 tests). It's
a UX rough edge.

## Root cause

`app/main.py` mounts `StaticFiles` at `/` ungated by design (today's P0
only gated the API routes, not the shell), so `index.html`/`app.js`
always load first; only the first data fetch (`/api/tree` etc.)
discovers there's no session and redirects to `/login` via `app.js`'s
`authFetch`.

## Extended 2026-07-17

This prompt reappears on *every* page refresh, even when already logged
in and even after previously dismissing it — not just on first visit.
Worse in Firefox specifically: Firefox doesn't support the File System
Access API the folder-picker needs, so the prompt is pure friction
there (the app's own text admits it - "den här webbläsaren stöder inte
mappval... men du kan fortsätta ändå").

## Real fix needs product input, not just code

- Should this be a one-time choice, persisted server-side (**not
  browser localStorage** — see POLICY.md if that ever gets added as a
  hard rule; for now just: prefer server-side state consistent with how
  the rest of this app handles persistence)?
- Should unsupported browsers skip the prompt entirely rather than show
  a "your browser can't do this" message every time?
- Separately, should the app do a lightweight session check (e.g. a
  `/whoami`-style call, or just always attempting the redirect-on-401
  flow) before rendering the onboarding prompt at all, so an
  unauthenticated visitor lands on `/login` first?
