# Deferred — photo-server

Explicitly out of scope until Phases 0–6 in [TODO.md](TODO.md) are
confirmed working end-to-end and Elisabeth has browsed, searched, tagged,
and downloaded at least one photo from outside the LAN. Listed here so
absence is a decision, not an oversight.

- **AI content and face recognition** — inference belongs on-device, on
  the phone; the server only stores derived tags/embeddings later, once
  there's something to sync. See [../VISION.md](../VISION.md) Pillar 2.
- **DynDNS automation** — manual IP/DNS updates are fine at two-user
  scale; automate only if it becomes a recurring chore.
- **Crop and soft-delete** — no destructive or edit workflow is needed
  for a browse-and-pick-for-download tool.
- **Perceptual-hash dedupe** — sha256 exact-match dedupe covers
  ingestion; near-duplicate clustering is quality-of-life, not required
  to get photos onto a USB stick.
- **Blur and monochrome tags** — not designed, not built, no schema
  reserved. Elisabeth judges quality herself while browsing (GUI spec
  amendment, see [MOCKUP.md](MOCKUP.md)).
- **Manual content-tagging endpoints** — schema exists (`tags.kind =
  'content'`), endpoints deferred. Only `kind = 'album'` endpoints are
  built now — see [DATA_DICTIONARY.md](DATA_DICTIONARY.md).
- **Share-link endpoints** — schema only for now (`share_links` table).
  No multi-party sharing needed with two known accounts. **Concrete need
  raised 2026-07-17**: Joakim wants to copy/paste/share a link to one
  specific picture. Checked what exists today: nothing — `app.js` has no
  URL routing for an individual photo view (no `pushState`/hash routing),
  and the only per-file URL (`/original?p=<relpath>`) requires an
  existing session for this account, has no "copy link" UI, and isn't a
  real app page (raw file, no gallery chrome). Real fix needs a design
  decision this project hasn't made yet: an authenticated deep-link
  (works only for someone already logged into this account - much
  smaller scope, no `share_links` table needed) vs. an actual public
  share link (works for anyone with the link, no login - the
  originally-scoped `share_links` feature, bigger scope, real access-
  control questions). Don't build either without picking one first.
- **In-app slideshow/casting UI** — v1's deliverable is a downloaded zip
  put onto a USB stick for a picture frame, not in-app display.
- **Usage-based fate prediction** — needs `audit_log` and album-tag
  history to accumulate first; a DPFAS-phase idea, not v1.
- **Revoke-all-sessions-by-user-id on password reset** — TODO.md 1.9b's
  admin password reset doesn't invalidate the reset user's existing
  refresh tokens, since Redis only indexes them by `jti`, not `user_id`.
  A stolen still-live session survives a reset until its own ≤12h expiry.
  Worth a Redis secondary index if this matters more than it does at
  two-user scale; not built now.
- **Self-service email-based password reset** — needs a self-hosted SMTP
  relay (system-level install) or a third-party email API (conflicts
  with this project's no-cloud-APIs rule); deferred indefinitely
  (2026-07-16). See TODO.md 1.9's admin-reset alternative, built instead.
- **Access-token revocation recheck, not just TTL expiry** (raised
  2026-07-17): `app/auth.py` (photo-viewer) and `auth_routes.py`'s
  `get_current_user` (backend) both trust a valid access-token JWT's
  signature+expiry alone — no per-request check against account/session
  state, so a revoked or disabled account stays usable for up to
  `ACCESS_TOKEN_EXPIRE_MINUTES` (currently 5, cut from 15 on 2026-07-17
  as a stopgap — see `server/app/tokens.py`'s comment) after revocation.
  The refresh token *is* rechecked every use (Redis-allowlisted), so the
  gap is bounded to one access-token lifetime, not unbounded. Real fix,
  not built today: either a Redis-backed access-token denylist (cheap,
  no Postgres round-trip) or the photo-viewer calling the backend's
  `/whoami` per request (simpler, adds a network hop per photo/thumbnail
  load — needs a latency check at real photo-browsing volume before
  adopting). Worth deciding once there's more than one active account.
- **`HARDWARE.md` may belong at `documentation/hardware/` instead of
  here** (raised 2026-07-17): the machine it describes hosts a ZFS pool
  "other things depend on" per its own text — broader scope than
  photo-server alone, even though today every actual reference to it
  (`DEPLOYMENT.md`, `TODO.md`, `README.md`) is from inside this folder.
  Not moved today: would mean updating those 3 cross-references under
  deadline pressure for a reorg that doesn't block P0. Revisit once
  another topic folder actually needs it, or as part of the P1
  `server/`→`backend/`, `app/`→`frontend/` restructuring already
  planned (see CHANGELOG 2026-07-17).
- **Pre-launch security review findings, not fixed today** (2026-07-17,
  reviewed before port-forwarding — see CHANGELOG). The
  `--proxy-headers`/rate-limiter and missing `--no-server-header` gaps
  found in the same pass *were* fixed (docker-compose.prod.yml). These
  two were not, deliberately — both are real but lower-severity, and
  fixing either correctly needs testing this session can't do (no live
  deployment yet, and this project's own precedent is that `docker
  compose up` is Joakim's action, not run by an AI session — see
  TODO.md 0.2):
  - **`app/Dockerfile` (photo-viewer) runs as root** — no `USER`
    directive, unlike `server/Dockerfile` which explicitly creates and
    switches to `appuser`. Defense-in-depth gap: an RCE-class bug
    anywhere in this container's dependencies would run as root instead
    of an unprivileged user. Not fixed today because doing it right
    means adding a non-root user *and* making sure the named volumes
    (`thumbcache`, `analytics_data`, `stories` — created at runtime via
    `Path.mkdir()`, not pre-baked into the image) are actually writable
    by that user, which needs a real container run to verify and isn't
    something to get wrong for the first time under deadline pressure.
    **Elevated priority 2026-07-17** (Joakim raised the actual blast-
    radius question this closes): combined with the LAN-egress gap
    directly below, this is step 2 of a real (if multi-step) chain from
    "app vulnerability" to "attacker has host-level access to the whole
    home LAN and router" — not just a generic hardening nice-to-have.
  - **No egress restriction from containers to the LAN** — confirmed
    2026-07-17 that none of the 5 services run `privileged` or
    `network_mode: host` (the biggest single mitigation - a compromised
    container can't trivially escape to the host through those), but
    Docker's default bridge networking still lets a compromised
    container make *outbound* connections to the LAN (192.168.1.0/24,
    including the router at 192.168.1.1) via the host's routing - nothing
    in `docker-compose.prod.yml` currently blocks that egress. Also
    relevant: Docker manipulates `iptables` directly and is known to
    bypass UFW's rules unless specifically configured for Docker - so
    DEPLOYMENT.md's UFW step protects inbound access only, not this.
    Real fix (not attempted today - needs real testing, not a rushed
    change to a live production compose file): egress-restrict the
    Docker network (e.g. an explicit `internal: true` network plus a
    narrow allow-list for the specific outbound calls each service
    actually needs - Let's Encrypt's ACME servers for Caddy, nothing for
    postgres/redis, nothing for auth/photo-viewer beyond the internal
    network itself).
  - **`/api/event` (photo-viewer) is intentionally unauthenticated**
    (telemetry only, returns no data — see `app/main.py`) but has no
    rate limiting either, unlike the auth backend's `/login`. Once this
    app is reachable from the open internet, anyone can spam this
    endpoint to grow `analytics.db` unboundedly or pollute usage
    analytics. Low severity (no data disclosure, no auth bypass) but
    real once port-forwarded. Fix would mean adding `slowapi` (or
    equivalent) to `requirements.txt` and wiring a limiter — deferred
    rather than adding a new dependency with limited time to test it.
- **Repo location on the server** — cloned to `~/differentiate-pictures-for-auto-sync`
  (Joakim's home dir) for speed under the 2026-07-17 deadline; Joakim
  would prefer a conventional service location (e.g. `/opt/photo-server`
  or `/srv/photo-server`). Purely a `mv` + updating `DEPLOYMENT.md`'s
  paths whenever there's time — nothing functional depends on it living
  in `~/`.
- **Single consolidated media root for P1+** (Joakim, 2026-07-17): today's
  fix pointed `PHOTOS_HOST_PATH` at Elisabeth's specific directory
  (`/tank/momfiles`) as a one-account stopgap. Future builds with
  more than one account's photos should live under one shared root
  instead (Joakim's example: `/tank/all_media_from_dpfas`), with
  per-account/per-owner scoping handled in the app layer rather than by
  pointing the whole container at a single person's folder. Ties
  directly into the already-noted "multi-tenant photo partitioning" gap
  right below — same underlying design question, not a separate one.
- **Multi-tenant photo partitioning / per-user sharing scope** — today's
  gate (`app/auth.py`) is deliberately binary: valid session or 401,
  with no per-user visibility restriction, because Elisabeth is the only
  account with photos in the pool (2026-07-17 P0 decision, see
  CHANGELOG). This was the right shortcut for one real user, but it's a
  shortcut: nothing today associates a photo with an owning account.
  Before a second real user (or the "share-link" entry above) is added,
  this needs actual design — which parts of `app/main.py`'s routes
  become user-scoped, whether photos need an owner column, and how that
  interacts with the still-schema-only `share_links` table. Flagging now
  so it's a deliberate next design pass, not a surprise retrofit.
