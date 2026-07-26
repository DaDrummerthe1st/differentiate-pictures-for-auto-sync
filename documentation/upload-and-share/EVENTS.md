# Event/party mode

Vision-level, thoroughly discussed 2026-07-26 — not scheduled, see [TODO.md](TODO.md). Feeds [../VISION.md](../VISION.md) Pillar 3 (presentation/sharing) with a concrete mechanism: "do you have any pictures? upload them to us!" — a host (wedding couple, funeral family, birthday) sets up an event; guests contribute; the event becomes the mechanism that brings new people into the network (Pillar 3's "opt-in for privilege" idea, applied concretely).

## QR code = event identity = auto-tag

The host generates a QR code for the event. It encodes a token resolving to that event's underlying tag (a `kind='album'` tag the host owns, see [../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md)'s reserved `events` table). Scanning it opens an upload page pre-scoped to that tag — every photo uploaded through it gets that tag applied automatically as its origin, before any other tagging happens. This is the same "batch = auto-tag" mechanism as a plain web upload ([UPLOAD.md](UPLOAD.md)), just pre-named by the host instead of typed by the uploader.

## Three independent axes

Confirmed as separate, not one combined preset — any combination is valid:

1. **Upload access** — host-configurable per event:
   - **Free-for-all**: anyone with the link/QR uploads, no account. Highest reach, immediately triggers the moderation/legal flag in [OWNERSHIP.md](OWNERSHIP.md) since truly anonymous strangers can upload. **Ownership, resolved 2026-07-26**: the uploaded photo's owner is the **event's own account** — a dedicated `users` row the event was set up with — never the anonymous guest, and never a claimable pending record (the `pending_shares` idea considered earlier for this case is dropped; that mechanism still stands for the unrelated email-invite share path in [SHARING.md](SHARING.md)). Keeps every anonymous contribution cleanly scoped to the event, separate from the host's own personal library, with one clear account holding moderation/legal responsibility for that event's pool until anything is shared onward from it.
   - **Pre-approved**: host invites specific people ahead of time (by email/username); only those accounts can upload.
   - **Register-then-approve**: anyone can sign up against the event, but the host approves each registrant before her uploads count/appear.
2. **Visibility scope** — independent of who uploaded or how: **all uploads visible** to every invitee, or a **curated best-of subset** (AI-assisted, human-reviewed, or both) that invitees see instead/in addition.
3. **Live TV-screen display** — a separate output channel entirely, not a visibility-scope setting: an on/off switch for showing a live feed (all uploads, or the curated subset — the host's call) on a screen at the venue, independent of the other two axes.

## Explicitly deferred to a later version

**Whether the host needs dedicated local hardware at the venue, or guests simply upload over the internet to the host's existing home NAS** — Joakim: "the hardware ownership is a later version altogether." This iteration's event uploads go to the same single server as everything else; no venue-local device is designed or built now.

## Open questions, not resolved — flag before building free-for-all upload

- **Legal reporting obligations** once strangers can upload without identity verification (see [OWNERSHIP.md](OWNERSHIP.md)'s Moderation section) — a lawyer question, not an engineering one. (Anonymous upload *ownership* is resolved, above — this is the one remaining blocker before build.)

## Status

Vision-level design, 2026-07-26. Not scheduled — see [TODO.md](TODO.md).
