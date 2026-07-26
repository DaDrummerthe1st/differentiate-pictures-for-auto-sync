# Sharing mechanisms

Three entry points, all converging on the same underlying grant (a `photo_owners` row for the sharee, or a `pending_shares` row — see [../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md) — if she doesn't have an account yet). Terms (strict/free) are set once per share and behave as described in [OWNERSHIP.md](OWNERSHIP.md) regardless of which of the three moved it.

## 1. Platform share sheet (primary)

```
User taps [Share] on a photo/album
  -> DPFAS shows a minimal terms step first
     (strict / free toggle, default free;
      this step can't be skipped — the OS
      share sheet has no concept of it)
  -> DPFAS generates a share token + link
  -> invokes the OS/browser Web Share API
     with that link
  -> OS share sheet opens (Messages,
     WhatsApp, Mail, AirDrop, ...)
  -> user picks a channel, link is sent
  -> recipient opens the link
     -> already a DPFAS user, logged in?
        -> photo/album appears as a
           pending share to accept
     -> not logged in / no account?
        -> falls through to the same
           invite+pending flow as email
           share, keyed by whichever
           account she logs into/creates
```

Fallback: if the Web Share API isn't available (older desktop browsers), the same terms step instead opens DPFAS's own in-app share dialog (below) rather than invoking a native sheet.

## 2. In-app share dialog (fallback, and the terms step above)

```
┌──────────────────────┐
│ Share with:           │
│ ( ) DPFAS username    │
│ ( ) Email address     │
│ [__________________]  │
│ Strict / Free   [ ]   │
│         [ Send ]      │
└──────────────────────┘

Username path:
  -> look up account by username
  -> exists? create photo_owners row
     for that user_id directly
     (shared_from_owner_id = sharer),
     terms = strict/free as chosen
  -> doesn't exist? "No user found"
     (usernames are exact-match,
      unlike the email path below)
```

## 3. Email invite (no account required to receive)

```
Owner shares to new@email.com
  -> pending_shares row created
     (email, photo_id or tag_id,
      terms, invited_by_user_id)
  -> invite email sent: signup link
  -> [recipient clicks link]
  -> creates a DPFAS account with
     that exact email
  -> on first login: any pending_shares
     rows matching her email resolve
     automatically -> real photo_owners
     rows created, no re-share needed
  -> if she never signs up: the share
     just sits pending, nothing is
     exposed to anyone, no fallback
     "view without an account" link
```

## Sharing a tag/album vs. a single picture

Both are shareable through all three mechanisms above. **Any tag, of any category,
is shareable as an album** — not only origin/event tags — see
[../tags/TAXONOMY.md](../tags/TAXONOMY.md)'s "every tag is a shareable album"
section, including the blur-preview review the owner sees before/while sharing.
Sharing a tag shares **live**, not a snapshot: the sharee sees whatever is currently
in that tag; later additions/removals by the owner propagate automatically (matches
an ongoing shared-album model). Each photo inside keeps its own strict/free terms
(the album-level default only applies at the moment a photo is added to it,
per-photo override always wins) — sharing the album doesn't silently change any
individual photo's terms.

## Tag verification/endorsement

Other users can corroborate a tag they didn't write — a face ID, a location, a
quality call — as a stronger signal than an unverified single-source tag, directly
serving the ML-training goal ([../VISION.md](../VISION.md) Pillar 2). Schema:
[../tags/SCHEMA.md](../tags/SCHEMA.md)'s `tag_endorsements` table — reserved this
iteration, no endpoints, same pattern as `share_links` today.

## Prior art considered

- **[Immich](https://selfhostable.dev/blog/immich-vs-photoprism-photo-management-2026/)**: has "partner sharing" (long-term person-to-person) and link-based shared albums. No asymmetric per-photo ownership terms (strict/free) — this project's ownership model ([OWNERSHIP.md](OWNERSHIP.md)) is more granular than existing self-hosted tools, not a reinvention of something that already exists.
- **Nextcloud Photos**: link/user/group sharing plus federation across instances — closest existing prior art for the eventual multi-node sharing story, worth revisiting once a second real node exists.

## Status

Designed 2026-07-26 (branch `upload-and-share`). No endpoints. See [TODO.md](TODO.md).
