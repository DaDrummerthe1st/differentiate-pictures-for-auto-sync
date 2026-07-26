# Event/party mode

Vision-level, thoroughly discussed 2026-07-26 — not scheduled, see [TODO.md](TODO.md). Feeds [../VISION.md](../VISION.md) Pillar 3 (presentation/sharing) with a concrete mechanism: "do you have any pictures? upload them to us!" — a host (wedding couple, funeral family, birthday) sets up an event; guests contribute; the event becomes the mechanism that brings new people into the network (Pillar 3's "opt-in for privilege" idea, applied concretely).

## QR code = event identity = auto-tag

The host generates a QR code for the event. It encodes a token resolving to that event's underlying tag (a `kind='album'` tag the host owns, see [../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md)'s reserved `events` table). Scanning it opens an upload page pre-scoped to that tag — every photo uploaded through it gets that tag applied automatically as its origin, before any other tagging happens. This is the same "batch = auto-tag" mechanism as a plain web upload ([UPLOAD.md](UPLOAD.md)), just pre-named by the host instead of typed by the uploader.

## Three independent axes

Confirmed as separate, not one combined preset — any combination is valid:

1. **Upload access** — host-configurable per event:
   - **Free-for-all**: anyone with the link/QR uploads, no account. Highest reach, immediately triggers the moderation/legal flag in [OWNERSHIP.md](OWNERSHIP.md) since truly anonymous strangers can upload.
   - **Pre-approved**: host invites specific people ahead of time (by email/username); only those accounts can upload.
   - **Register-then-approve**: anyone can sign up against the event, but the host approves each registrant before her uploads count/appear.
   *(Who owns an anonymous free-for-all upload is not yet resolved — see Open questions below.)*
2. **Visibility scope** — independent of who uploaded or how: **all uploads visible** to every invitee, or a **curated best-of subset** (AI-assisted, human-reviewed, or both) that invitees see instead/in addition.
3. **Live TV-screen display** — a separate output channel entirely, not a visibility-scope setting: an on/off switch for showing a live feed (all uploads, or the curated subset — the host's call) on a screen at the venue, independent of the other two axes.

## Explicitly deferred to a later version

**Whether the host needs dedicated local hardware at the venue, or guests simply upload over the internet to the host's existing home NAS** — Joakim: "the hardware ownership is a later version altogether." This iteration's event uploads go to the same single server as everything else; no venue-local device is designed or built now.

## Open questions, not resolved — flag before building free-for-all upload

- **Anonymous upload ownership**: with no account, who is `photo_owners.user_id`? Proposed (not yet confirmed): reuse the `pending_shares` mechanism ([SHARING.md](SHARING.md)) — even a free-for-all upload asks for at least a name/email, creating a claimable pending-owner record the uploader can later attach a real account to, rather than truly ownerless photos. Needs explicit confirmation before it's built.
- **Legal reporting obligations** once strangers can upload without identity verification (see [OWNERSHIP.md](OWNERSHIP.md)'s Moderation section) — a lawyer question, not an engineering one.

## Status

Vision-level design, 2026-07-26. Not scheduled — see [TODO.md](TODO.md).
