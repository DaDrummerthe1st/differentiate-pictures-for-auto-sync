# Thumbnail img tags have no silent-refresh on expired access token

Status: **confirmed as a real, everyday bug (2026-07-19), not fixed**.
Originally found alongside a Redis restart
(`2026-07-18-redis-has-no-persistent-volume-every-restart-wipes-active-sessions.md`),
but this update confirms it also happens with no restart involved at
all - answers this file's own "next session should start with" question.

## Confirmed 2026-07-19: happens in normal, uninterrupted browsing too

Joakim hit this live during a long GUI-debugging session with no server
restart anywhere in between - screenshot showed every `/thumb?p=...`
request returning a clean `401`, all grid thumbnails broken. Access
token had simply expired (5 min) mid-session. Reloading the page
self-healed it (`/api/tree`'s fetch goes through `authFetch`'s silent
refresh, which runs before `renderTree()` builds any `<img>` tags), so
no re-login was needed - but the underlying gap is real and will recur
for any browsing session longer than 5 minutes. Priority raised
accordingly; not fixed this session either (deliberately deferred so
the session already in progress could wrap up) - next session should
pick one of the two options below rather than re-investigate whether
this is worth fixing.

## Symptom

Same incident as the Redis report: a solid streak of `401 Unauthorized`
on `/thumb` requests in `photo-viewer`'s logs, with no recovery until
the user manually logged in again.

## Investigation log

1. `app/static/app.js` reviewed: `authFetch()` is the *only* place with
   silent-refresh-and-retry logic on a 401 (calls `/refresh`, retries
   the original request once, only bounces to `/login` if the refresh
   itself also fails).
2. Grid thumbnails are rendered as plain `<img>` elements
   (`renderTree()`: `imgEl.src = /thumb?p=${encodeURIComponent(img)}`)
   - the browser fetches these directly via the `src` attribute, with
   cookies attached automatically, but this **never goes through
   `authFetch`**. Same for the lightbox's `<img id="lbImg">` full-size
   view.
3. This means: today's incident (Redis wiped, refresh tokens dead) is
   one way to hit this, but it's not the only one - the access token's
   normal 5-minute expiry alone, mid-browsing-session, with Redis
   perfectly healthy, would produce the identical symptom (thumbnails
   suddenly all showing broken/401) with no restart involved at all.
   Not yet confirmed happening in the wild outside today's incident, but
   the code path clearly allows it.

## Leading theory (confirmed mechanism, real-world frequency unconfirmed)

`<img>`-tag requests bypass this app's only 401-recovery path entirely.
Every `fetch()`-based call (`/api/tree`, `saveImage`'s download fetch,
voiceover endpoints) gets silent renewal; thumbnails and the lightbox's
full-size image do not.

## Fix, not built yet

Needs a design decision, not a guess: options include (a) proactively
refresh the access token on a timer client-side before it expires,
independent of any particular request 401-ing, so `<img>` tags never
hit an expired token in normal use, or (b) on detecting broken thumbnail
loads (e.g. an `onerror` handler per `<img>`), trigger the same
`authFetch`-style refresh-and-retry, reloading just the failed images.
(a) is simpler and prevents the problem outright; (b) is reactive and
only fixes it after the user's already seen broken images. Not built
this session - flagged for a future session with the design call made
explicitly, per this repo's "don't guess at live design decisions" norm.

## Next session should start with

Confirm real-world frequency first: does this actually happen during
a normal, uninterrupted browsing session longer than 5 minutes (no
restart involved)? If Joakim or Elisabeth can reproduce broken
thumbnails mid-session without any server restart, that upgrades this
from "a mechanism that exists" to "a real, everyday bug" and raises its
priority accordingly.
