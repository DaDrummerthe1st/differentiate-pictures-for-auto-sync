# Changelog

One entry per revision, newest first.

## 2026-07-15 (10)

- Trimmed two cross-file/within-file duplications found while auditing
  `documentation/` for excess length at Joakim's request: `VISION.md`
  Pillar 3 fully restated the closed-vs-opt-in trust-boundary tension
  already owned by `POLICY.md`'s Open questions section (POLICY.md's own
  rule: nothing project-wide duplicates outside it) — now a one-line
  pointer. `photo-server/README.md` repeated its own Non-negotiables
  Postgres/pgvector reasoning in its closing paragraph — now stated
  once. No information removed, only the second copy of each fact.
  Char counts (codepoints): `VISION.md` 3718 → 3483 (−235),
  `photo-server/README.md` 4057 → 4016 (−41); −276 net.

## 2026-07-15 (9)

- Fixed a scope mismatch Joakim spotted by auditing every root
  `documentation/` folder against its own stated purpose:
  `photo-server/DPFAS_VISION.md` opened with "the standing goal across
  the whole project," directly contradicting its own folder's README
  ("one narrow, closed slice... nothing here should grow toward...
  AI-driven curation suggestions"), and its three-UX-path table
  duplicated `DATA_DICTIONARY.md`'s Tag-dimensions table in the same
  folder. Deleted the file (per Joakim's choice among three options
  offered); its only non-duplicated content — the Postgres/pgvector
  rationale — moved into `photo-server/README.md`'s existing
  "Relationship to the wider vision" section; the "standing goal" framing
  and three-path breakdown now live in `VISION.md`'s Pillar 2, the
  correct project-wide home. Updated the three other files that linked
  to the deleted file (`VISION.md`, `photo-server/DEFERRED.md`,
  `picture-handling/TODO.md`) to point at `VISION.md` Pillar 2 instead.
  Audited every other file in every root folder against its own folder's
  stated scope; found no other mismatches. `documentation/`: 39,976 →
  39,215 characters.

## 2026-07-15 (8)

- Untracked 5 `.pyc` files under `app/*/__pycache__/` that were
  committed before `__pycache__/` was added to `.gitignore` last
  entry — `git rm --cached`, files kept on disk. Confirmed via
  `git ls-files -i -c --exclude-standard` that nothing else tracked
  matches any `.gitignore` pattern.
- Researched current CVEs (real web search, not training-data guesses)
  for every package in `requirements.txt`, which had no version pins at
  all, and pinned each to the latest patched release: `Pillow==12.3.0`
  (fixes CVE-2026-25990, CVE-2026-42308, CVE-2026-42309, CVE-2026-55379,
  CVE-2026-55380), `mysql-connector-python==9.7.0` (well past
  CVE-2024-21272 and CVE-2025-21548), `numpy==2.5.1`, `opencv-python==5.0.0.93`
  (bundles a libwebp/libvpx build; 5.0.0.93 is current),
  `exif==1.6.1` and `python-magic==0.4.27` (both already the latest
  release on PyPI — no newer version exists, no known CVEs found for
  either). **Unverified**: this sandbox has no `pip`/`ensurepip`, so
  none of this could actually be installed and run against `app/` —
  numpy 2.x and opencv-python 5.x are major version bumps with real
  breaking-change risk (numpy 2.0's ABI break in particular). Flagged in
  `picture-handling/TODO.md`'s Known Drift for Joakim to verify on a
  machine with pip before trusting it. Also noted, but deliberately not
  acted on (system-level, outside this session's authority per
  POLICY.md): Python 3.12.13 is the current security-patch release for
  this repo's 3.12 branch, vs. the 3.12.3 recorded in
  `photo-server/HARDWARE.md`.
  `documentation/`: 39,441 → 39,976 characters.

## 2026-07-15 (7)

- Added `tools/doc_metrics/`: TDD'd (stdlib `unittest`, pytest isn't
  installed in this environment) character-count logging so the
  character-count-change rule is measured the same way every time
  instead of ad hoc `wc -c`. `metrics.py` counts Unicode codepoints per
  `*.md` file; `log.py` snapshots the current commit (or `--backfill`s
  the full history via read-only `git show`/`git ls-tree`, never
  touching the working tree); `report.py` prints char count, delta, and
  an approximate token count (chars/4, explicitly labeled as directional
  only — real cost also depends on current model pricing, not tracked
  here) per commit. `metrics.jsonl` is git-tracked (the durable record,
  per the self-sufficiency rule); `metrics.db` (SQLite) is gitignored,
  local, and rebuildable from the jsonl via `--rebuild-db`. Backfilled
  all 77 existing commits. Also fixed two `.gitignore` gaps found while
  doing this: `.claude/settings.local.json` was untracked but not
  ignored (risk of accidentally committing local permission config), and
  `__pycache__/` wasn't ignored anywhere. Corrected the character-count
  methodology itself: earlier entries in this file used `wc -c` (byte
  count), which runs ~0.8% high on this repo's docs because of em
  dashes; from here on, counts are Unicode codepoints via this tool —
  noted as a one-time methodology switch, not a discrepancy to chase.
  `documentation/`: 39,113 characters (codepoint count, not directly
  comparable to prior entries' byte counts). `CLAUDE.md`: 6,178
  characters.

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
