# Changelog

One entry per revision, newest first.

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
