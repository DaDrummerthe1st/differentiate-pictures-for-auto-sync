# Sharing permissions and abuse mitigation

Paper design, 2026-07-28. Covers consent-to-receive-a-share, blocking, and the unsolved unsolicited-explicit-content problem — distinct from [OWNERSHIP.md](OWNERSHIP.md)'s strict/free/leased axis, which governs *redistribution* of legitimate content, not whether a share should reach someone at all.

## Mutual acceptance, default

Every incoming share requires an explicit accept, across all three [SHARING.md](SHARING.md) entry points — including the username path, which today creates the `photo_owners` row immediately with no consent step at all; that's a real gap this closes, not just a new policy layered on top. A per-user `users.sharing_policy` setting (`mutual_accept` default, `open` opt-in) lets a user skip her own accept step for convenience.

**`open` is gated, not shippable yet**: see "Unsolicited explicit content" below — no opt-out ships until an automated receive-time filter exists. Decided 2026-07-28.

## Blocking

A `blocked_users` table (`blocker_user_id`, `blocked_user_id`, `created_at`). A block always overrides the target's `sharing_policy` — a blocked sender can never create a new share/invite toward the blocker, `open` mode or not. Whether the blocker also loses her own visibility into that sender's *past* shares is a separate, blocker's-own choice (hide/leave), independent of the strict/free/leased tier still governing the underlying grant itself.

**Not decided**: whether a blocked sender gets a silent failure or an explicit "you're blocked" message when she tries to share. Real precedent both ways (historically silent on Twitter/X; explicit on some other platforms) and a genuine anti-retaliation UX call — not made here.

## Unsolicited explicit content, worst case involving minors — candid status

No clean technical fix exists for **novel** (previously-unflagged) content sent through a channel the recipient already accepted, or via an `open`-mode account — this is a real, industry-wide gap, not something this project can uniquely solve. [OWNERSHIP.md](OWNERSHIP.md)'s PDQ perceptual-hash blocklist only catches material someone has already flagged elsewhere; it does nothing against first-generation content.

The one mitigation that actually targets *novel* content is an on-device nudity/NCII classifier that blurs or warns before display — this repoints [../tags/TODO.md](../tags/TODO.md)'s already-flagged "nudity auto-detection" from a tagging feature into a receive-time filter, not a new idea, just a new use for it. Until that exists: **mutual-acceptance stays mandatory, no `open` opt-out** — decided 2026-07-28, over shipping the convenience opt-out now and accepting the risk in the meantime.

For minors specifically, this stays a legal/human-moderation problem, not an engineering one — same stance [../policies/POLICY.md](../policies/POLICY.md) already takes on the anonymous-upload event mode.

## Considered and rejected: cross-identity fingerprinting

Idea raised: fingerprint device/browser/metadata signals so a repeat-blocked user who signs up under a new email gets recognized and auto-blocked again.

**Rejected 2026-07-28.** It contradicts this project's own closed-by-default, no-telemetry privacy stance ([../policies/POLICY.md](../policies/POLICY.md)) — it's the same covert cross-account correlation technique ad-tech/anti-fraud tooling uses, aimed at bad actors but paid for by continuously collecting signal on *every* user, since there's no way to know in advance who'll eventually be blocked. It's also a poor technical trade: a determined bad actor rotates devices/IPs/browsers trivially, while false positives land more reliably on ordinary users (a shared household device/IP looking like "the same blocked person") than on the rare persistent abuser. At this project's actual current scope (one household plus invited relatives, not an open stranger network), mutual-acceptance-by-default plus blocking already covers the realistic threat — this is really a Pillar 3 stranger-scale problem, and [../policies/POLICY.md](../policies/POLICY.md) already gates that entire mode behind real legal grounding before it ships at all. Not kept as an open question to revisit; recorded here so the reasoning isn't lost if it resurfaces.

## Status

Paper design, 2026-07-28. No schema migration, no endpoints. See [TODO.md](TODO.md).
