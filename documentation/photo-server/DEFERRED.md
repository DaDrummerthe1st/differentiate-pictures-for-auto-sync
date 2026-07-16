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
