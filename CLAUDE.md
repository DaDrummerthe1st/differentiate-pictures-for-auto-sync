# Working agreement

This file is the working agreement between Joakim and any AI session (or
future human contributor) working in this repo. The repo is the memory —
see the self-sufficiency rule below.

## Non-negotiables

- **Security and privacy first**: consider it for every change, not just
  ones that look security-related. This app handles personal photos and
  EXIF/GPS metadata, and is heading toward a distributed system that will
  hold other people's data too — privacy is a first-class constraint from
  day one, not something bolted on once sync exists.
- **Test-Driven Development**: write a failing test before the
  implementation for new functionality where practical. Run the FULL test
  suite before every commit, even for changes that look unrelated or
  untestable (e.g. a config or docs-only edit) — cheap insurance against
  regressions that aren't obvious from reading the diff.
- **Ask or search — never guess.** If a fact is unknown or uncertain (a
  library's current API/version, a legal/compliance detail, a business
  rule, anything project-specific not already stated here) stop and either
  ask directly or run a real web search. Never present an assumption or a
  plausible-sounding guess as fact.
- **This repo is fully self-sufficient — no external memory required.** A
  human developer, or a fresh AI session with zero prior context, must be
  able to pick this project up entirely from what's checked in here.
  Decision history, status, future plans, and reusable lessons belong in
  this repo (CLAUDE.md, POLICY.md, CHANGELOG.md, the relevant
  README/TODO per topic) — never only in a private/local AI memory store.
- **Documentation stays current**: when a change affects schema, API
  surface, or architecture, update the relevant doc in the same pass —
  don't let docs drift from what the code does. (Known existing drift:
  see [documentation/picture-handling/TODO.md](documentation/picture-handling/TODO.md)
  for the MySQL-vs-PostgreSQL mismatch.)
- **Lean, exact, and compact**: no filler, no restating what's already
  documented elsewhere, no speculative abstraction for hypothetical
  future needs. Prefer the more precise word or number over the vaguer
  one — effective text over more text. Documentation should be thorough
  but slim — sectioned, skimmable, no duplication between files.
  Cross-references must terminate: a "see X for why" pointer has to land
  on the actual explanation, not on another pointer back — that's a
  circular reference, not a cross-reference, and it silently loses the
  information both files were supposed to preserve (caught once in
  README.md ↔ HARDWARE.md; check for it whenever adding a "see X" link).
- **One revision per update**: add a new entry to the top of
  CHANGELOG.md for every meaningful change (what + why, one or two
  lines) — newest first. Never rewrite or reorder past entries.
- **Report the character-count change** for every documentation edit —
  before → after count for the file or folder touched, in the
  CHANGELOG.md entry and in the session's closing summary. Makes drift
  and bloat visible over time instead of assumed. Measure it with
  [tools/doc_metrics](tools/doc_metrics/README.md) (`log.py` after
  committing, `report.py` to see the trend) rather than ad hoc `wc`
  calls, so every session's numbers use the same method and stay
  comparable to each other.
- **Log the real token/dollar cost of every commit** — run
  [tools/commit_cost](tools/commit_cost/README.md)'s `log.py` after
  committing (same discipline as `doc_metrics` above), commit the
  resulting `commit_costs.jsonl` update. This reads actual billed usage
  from Claude Code's own session transcripts, not an estimate — see that
  tool's README for what it can and can't tell you (e.g. human-authored
  commits log a real `0`, not "unknown").
- **Commit continuously**: commit coherent chunks of work as you go, not
  one giant commit at the end of a session. This is standing
  authorization to commit without asking first. It does NOT cover push,
  force-push, history rewrites, or any other high-blast-radius action
  (defined below) — those are never run directly, only ever handed over
  as a copyable command for Joakim to run himself.
- **Argue with evidence**: if a proposal (naming, structure, approach)
  has a concrete best-practice or precedent-based counter-argument, raise
  it and explain the trade-off before implementing it as asked — don't
  default to agreement, and don't silently substitute your own
  preference either.
- **Ask for constraints before high-blast-radius work**, rather than
  waiting for them to surface organically mid-task.
- **Copyable text goes in one fenced code block** — any text meant to be
  copied verbatim (commands, handoff prompts, etc.), never inline prose
  mixed with bold/headers.
- **End substantive sessions with both a durable record and a chat
  summary.**

## What counts as high-blast-radius here

Human-in-the-loop required — draft the action, hand it over, don't
execute it directly:

- **Running the app against the real photo library.** The discard / save
  / mark workflow moves and deletes actual files. Only run it against
  `resources/testpics` (or other clearly-disposable fixtures) without
  asking first.
- **Database schema changes** — `CREATE`/`ALTER`/`DROP` or anything else
  structural, and anything touching the gitignored credentials in
  `app/local_mysql.py` (name is legacy — see the Postgres note in
  [documentation/picture-handling/TODO.md](documentation/picture-handling/TODO.md)).
- **Any system-level install, config, or deployment** — see
  [policies/POLICY.md](documentation/policies/POLICY.md) ("Deployment
  and system access") for the full rule; hand to Joakim as copyable
  commands, never run directly.
- **`git push`, force-push, or any history rewrite.**

Everything else — local edits, running the test suite, committing to the
current branch — is fine to do without asking each time.

## Branching and merging

- **New branch, ask first.** Before starting non-trivial new development
  work (a new TODO.md step, a feature, anything beyond a small fix), ask
  whether to create a new branch and suggest one — don't assume the
  current branch is the right place for it.
- **Merging into main needs confirmation, every time.** Never merge a
  branch into main without asking first. Unlike push/force-push/history
  rewrites above (always handed over as a copyable command, never run
  directly), a merge can be run directly once Joakim confirms — the
  confirmation itself is the authorization, not a request to hand over
  the command.

## Documentation layout

- `documentation/` — every subfolder (root included) has its own
  `README.md`: what the folder is for, plus an index of its children
  only if that index adds something a reader wouldn't already get from
  each child's own opening line.
- `documentation/policies/POLICY.md` (not `README.md` — a deliberate
  naming exception so "hard rules live here" is unmistakable) holds
  genuinely project-wide hard constraints. Nothing project-wide gets
  duplicated outside this file.
- **Topic folders** (a subject with its own ongoing open work) get a
  mandatory `TODO.md` — open/deferred items, or "nothing planned right
  now" if empty. Never delete it for being empty; the point is proving
  absence was checked. Pure reference folders (like `policies/`) don't
  need one.
- Root `README.md` is the public-facing GitHub landing page (short pitch
  + pointer into `documentation/`); this file (`CLAUDE.md`) is the
  working agreement for whoever — human or AI — is doing the work.
