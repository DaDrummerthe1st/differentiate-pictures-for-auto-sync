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
  No multi-party sharing needed with two known accounts.
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
