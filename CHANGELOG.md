# Changelog

One entry per revision, newest first.

## 2026-07-15 (6)

- Captured Joakim's long-term system vision (four pillars: distributed
  storage/DFS with a blockchain-like stability mechanism, metadata/
  search/curation, presentation and event-based sharing with an opt-in
  privilege-for-data-sharing model, and multi-angle event reconstruction)
  in a new project-wide `documentation/VISION.md`, cross-linked from
  `distributed-sync/README.md`, `photo-server/README.md`,
  `photo-server/DPFAS_VISION.md`, and the top-level `documentation/
  README.md` index, rather than duplicated into any of them. Flagged
  Pillar 3's opt-in-sharing model as an open tension against the current
  closed-by-default posture in `POLICY.md`'s open questions. Added the
  Sunday deadline's real context to `photo-server/README.md`: a memorial
  for Per, Elisabeth's mother's late partner, where she wants to pick
  photos from ripped CDs/DVDs for a picture-frame USB stick — this is
  why v1 stops at browse/search/tag/download and nothing more.
  `documentation/`: 33,899 → 39,441 characters.

## 2026-07-15 (5)

- Absorbed two external planning documents (a photo-server build plan and
  a GUI-spec amendment, both supplied in chat) into a new
  `documentation/photo-server/` topic folder: README, TODO (the granular
  TDD roadmap), HARDWARE, DATA_DICTIONARY, DEFERRED, DPFAS_VISION, and
  MOCKUP (bare-minimum login + thumbnail-screen written spec, no code).
  Sequenced the roadmap so login (Phases 0–1) is complete before any
  photo/catalogue work starts, per Joakim's priority. Flagged one
  inference for confirmation: the original `selections` table is treated
  as dropped in favor of the GUI spec's tag-based (`kind='album'`)
  mark/download mechanism, since both solved the same problem — see
  DATA_DICTIONARY.md. Superseded the "first MVP/POC, purpose undefined"
  item and its speculative UI/database/AI sections in
  `picture-handling/TODO.md` with a pointer to the new folder, now that
  the purpose is decided. Added two CLAUDE.md rules: report the
  character-count change for every documentation edit, and tightened
  "Lean and compact" into "Lean, exact, and compact." Done on a new
  `photo-server-planning` branch, not master, per Joakim's request.
  `documentation/`: 8,249 → 33,899 characters. `CLAUDE.md`: 5,624 → 5,986
  characters.

## 2026-07-15 (4)

- Second pass on the same documentation trim, per Joakim's answers to a
  few judgment calls: dropped the "In use?" column from both external-
  tools tables (all rows read "Not yet" — zero information), tightened
  a couple more sentences, and removed the sudo/deployment rule
  restatement from CLAUDE.md's high-blast-radius list in favor of a
  pointer to POLICY.md's "Deployment and system access" section (POLICY.md
  already declares itself the sole home for that rule). Declined:
  merging each topic's README+TODO into one file (keeps the documented
  structure rule intact) and resolving the "4D" placeholder in
  `picture-handling/TODO.md` (still unclear — left as-is).
  8,430 → 8,249 characters in `documentation/`.

## 2026-07-15 (3)

- Trimmed `documentation/` for redundancy: the "roadmap addendum
  expected from Joakim" note was stated near-verbatim in three files
  (distributed-sync README, its TODO, and POLICY.md) — now stated once
  in TODO.md's open question, with the other two pointing at it. Also
  de-duplicated a NAS-spec restatement and a security/privacy-posture
  restatement, and tightened wordy passages in `picture-handling/TODO.md`
  and the top-level `documentation/README.md`. No meaning changed; the
  SETI@home analogy was deliberately kept since it's the origin of the
  idea, not just flavor text. 8,950 → 8,430 characters.

## 2026-07-15 (2)

- Noted the next session's starting point in
  `documentation/picture-handling/TODO.md`: build the first frontend
  MVP/POC, operating on pictures already on this server, for a specific
  purpose still to be defined with Joakim. No code written this session.

## 2026-07-15

- Initialized the working-agreement and documentation structure:
  `CLAUDE.md` (non-negotiables + high-blast-radius definition), root
  `README.md`, `documentation/` (policies, picture-handling,
  distributed-sync), and this changelog. Retired `docs/` and
  `resources/for documentation/`, folding their content into the new
  structure. Done to make the repo self-sufficient for future sessions
  instead of relying on AI memory.
