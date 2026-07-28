# TODO — security

Open items needing real resolution — captured so absence is a decision, not an
oversight, per this project's documentation-layout rule.

- **Facial-recognition/detection data security under a future DFS/multi-location
  world** (THREATS.md #6) — raised 2026-07-27, explicitly **not answered by
  guessing or synthesizing from general knowledge**. Joakim's instruction: the
  session that picks this up must actually search the internet and cite
  well-renowned, authoritative sources only (established security research orgs,
  academic work, recognized standards bodies — not random blog posts or
  SEO-optimized listicles) before proposing anything. Log the lookups per this
  project's research-log convention (`~/.claude/CLAUDE.md`'s "Log every external
  research lookup" rule) so the sources are traceable from this decision, not just
  asserted. Concretely: once a photo's bounding-box/face data can live on hardware
  the photo's *subject* doesn't control (someone else's home NAS holding a
  redundant copy), what does the field actually recommend — encryption-at-rest
  keyed so only the owner can decrypt (already sketched informally in the
  ownership-model discussion, [distributed-sync/TODO.md](../distributed-sync/TODO.md)),
  something more specific to biometric-adjacent data (GDPR treats this as a
  special category in the EU — is that relevant here even for a non-EU-hosted
  personal project?), or something else entirely. Out of scope for current design
  work per VISION.md's just-reaffirmed scope note (this is Pillar 1/DFS territory)
  — fine to research and design on paper ahead of time if picked up.
- **Third-party tagging consent** (THREATS.md #4) — no design yet for a tagged
  person (linked-account or local-only) to see, object to, remove, or block a tag
  that names/links her. Needs a real design pass, likely alongside
  [tags/UX_FLOWS.md](../tags/UX_FLOWS.md)'s existing invite-CTA flow rather than
  as a separate mechanism.
- **Server-side bounding-box validation** (THREATS.md #2) and **stored-XSS
  discipline for tag text** (THREATS.md #3) — both straightforward once real
  endpoints/GUI exist; capture as explicit TDD test cases at that point rather
  than trusting mockup-era discipline to carry over.
- **Should labeled face-detection data (bounding box + person tag) get a
  stricter access bar than ordinary photo data**, not just the same
  closed-by-default rule everything else gets (THREATS.md #1)? Undecided.
- **Auth hardening** (THREATS.md #10) — a compromised account inherits every
  privilege this design assumes only its legitimate owner has (leased-tier
  decrypt keys, private tags, item 6's face-matching reference embeddings if
  built). Needs a real design pass (password hashing, rate limiting/lockout,
  session/token management, MFA) before any sharing/DFS feature ships for
  real. Raised 2026-07-28/29 during tag/sharing design; not resolved here.

## Status

Opened 2026-07-27, alongside [README.md](README.md) and [THREATS.md](THREATS.md).
