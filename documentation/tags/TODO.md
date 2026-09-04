# TODO — tags

Open items, not designed or scheduled — captured so absence is a decision, not an
oversight, per this project's documentation-layout rule. Nothing below has a
numbered build step yet; see [../photo-server/TODO.md](../photo-server/TODO.md)
Phase 5 for the one piece (origin/`kind='album'`) already partially built.

- **User bio for tag suggestions** (raised 2026-07-27, future idea only — Joakim
  explicitly deferred designing this now): inviting the user to write a few lines
  about herself — hobbies, occupation, family situation — to help both suggest tags
  on her own photos and help her find others' publicly-shared photos that match her
  interests. Not designed: where it lives (a profile doc doesn't exist yet), how it
  feeds tag suggestions, privacy implications of a bio itself being searchable data.
- **Contacts import** (raised 2026-07-27, future idea only): letting the app ask
  permission to read the user's phone contacts to help pre-populate/match
  local-only person entities when tagging. Not designed: permission flow, whether
  imported contacts become entities automatically or only on confirmation, how this
  interacts with the invite CTA in [UX_FLOWS.md](UX_FLOWS.md). **Privacy constraints
  flagged 2026-09-04**: browser Contact Picker API over native `READ_CONTACTS` (no
  native app planned anyway), plus three hard rules once this is built — see
  [../security/THREATS.md](../security/THREATS.md) row 17.
- **Nudity/sensitive-content auto-detection** for the privacy category
  (TAXONOMY.md's "automatically tagged private" case): on-device inference, DPFAS
  phase — ties to [../VISION.md](../VISION.md) Pillar 2's face/object recognition
  work, not started; catalogued as its own row in
  [../curation/DETECTORS.md](../curation/DETECTORS.md)'s privacy/safety section. Until this exists, the privacy category's specific semantic
  tags (`nudes`, a children's-photo tag) are manually applied, not automatic.
- **Reconciling `kind` (`album`/`content`) against the new `category` column**
  (SCHEMA.md's `tags` table): whether `kind` collapses into a derived property (any
  tag is shareable/downloadable once `category` exists, per TAXONOMY.md) or stays a
  separate mechanical flag alongside category is an implementation-time decision,
  not made here.
- **Entity merge/dedup**: no flow designed yet for correcting two separately-created
  `entities` rows that turn out to be the same person/object/animal/place (e.g. "Dad"
  tagged once via autocomplete and once as a fresh entity by mistake). Matters
  directly for the "search all photos of my dog" use case this taxonomy exists to
  serve — an unmerged duplicate silently splits that search in two. Not designed.
  **Trigger mechanism sketched 2026-08-05** (Joakim's own example: he types "Joakim"
  once, "Jocke" another time, for the same person): **name-string similarity alone
  won't catch this** — "Jocke" and "Joakim" share no useful substring, and nicknames
  are culturally arbitrary, not a string-distance problem. The reliable trigger is
  **embedding similarity**: if a newly-confirmed entity's reference embedding lands
  very close, in embedding space, to an existing entity's reference embedding
  (same underlying face/animal, regardless of what name was typed), surface a "these
  might be the same — merge?" prompt — never auto-merge, same motivated-tagging
  principle as everything else. Reuses the nearest-neighbor mechanism already
  designed for identity matching itself
  ([../curation/IDENTITY_MATCHING.md](../curation/IDENTITY_MATCHING.md)), just run against
  the user's own other entities instead of against unlabeled crops. Still not
  designed: the actual merge operation (repointing every `tag_references` row from
  the losing entity to the winning one), and what happens if the two entities
  already disagree on an attribute (e.g. different breed guesses for the same
  animal).
- **Search ranking/depth tuning** for the relationship-graph walk (TAXONOMY.md's
  "Search walks the relationship graph" section): the 2-hop default is a starting
  guess, not tested against a real tag graph. Revisit once there's one to test
  against.

## Status

Opened 2026-07-27, alongside [TAXONOMY.md](TAXONOMY.md)/[SCHEMA.md](SCHEMA.md)/[UX_FLOWS.md](UX_FLOWS.md).
Nothing here blocks that design work — these are extensions/follow-ons, not
prerequisites.
