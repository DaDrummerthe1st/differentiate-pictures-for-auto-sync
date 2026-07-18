# Working agreement

This file is the working agreement between Joakim and any AI session (or
future human contributor) working in this repo. The repo is the memory —
see the self-sufficiency rule below.

## Non-negotiables

- **Security and privacy first**: consider it for every change, not just
  ones that look security-related — a first-class constraint from day
  one, not something bolted on later. Specifics (what data is sensitive,
  why) live in [POLICY.md](documentation/policies/POLICY.md), not
  repeated here.
- **Test-Driven Development, no exceptions for "small" or "obvious"
  code**: write a failing test before the implementation, every time,
  confirm it actually fails for the expected reason, then implement.
  "Where practical" used to qualify this bullet; dropped 2026-07-16
  after a real slip during photo-server Phase 1 — a one-off helper
  (`app/audit.py`'s `log_audit_event`) got written before its test, on
  the reasoning that it was small enough not to matter. Disclosing the
  slip in the moment was right; that a later, unrelated code-review pass
  over the same area then caught a real bug (`app/db.py`'s `get_db()`
  silently dropping commits on an exception path) does not retroactively
  excuse having skipped the test — reviewed-and-lucky isn't the same as
  tested. Run the FULL test suite before every commit, even for changes
  that look unrelated or untestable (e.g. a config or docs-only edit) —
  cheap insurance against regressions that aren't obvious from reading
  the diff.
- **Check for newest dependency versions before every numbered TODO
  step** (0.1, 0.2, 1.3, etc. — not just once per phase), not only when a
  CVE prompts it. If a newer version is available, update to it as part
  of that step rather than starting the step on a stale pin. If the
  newer version turns out incompatible or breaks a test once updated,
  fixing that break is itself the priority — don't quietly revert to the
  old pin and move on; the step isn't done until the suite is green on
  the current version. Decided 2026-07-16.
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
- **Never claim a file was edited/logged/fixed without checking it
  against the tool calls actually made that turn.** Before sending any
  reply that says "logged," "added," "fixed," or similar about a
  specific file, verify the corresponding Edit/Write tool call actually
  ran in this turn — don't infer it from intent or from having
  described the plan in the response text. Decided 2026-07-18 after
  telling Joakim a `DATA_DICTIONARY.md` edit had been made when it
  hadn't (planned and described mid-reply, but the actual tool call was
  never issued — a large multi-topic reply describing several file
  edits together was the trigger, see
  `documentation/bugs/claude/2026-07-18-claimed-a-doc-edit-was-made-when-it-wasn-t.md`).
  This repo *is* the durable record for anything discussed in a
  session — a false "done" claim isn't a small slip, it's a hole in the
  only safety net that exists.
- **A promised follow-up gets a TodoWrite item, not just a sentence.**
  Whenever a reply says something like "I'll present this for
  confirmation," "I'll come back to this," or "let me get back to you
  on X" — add a `TodoWrite` item for it in that same turn, don't just
  state it in prose. Decided 2026-07-18 after a thumbnail-precompile
  design synthesis was promised back to Joakim for confirmation, then
  silently dropped when several unrelated messages and a live incident
  arrived immediately after — it only surfaced later via the session's
  wrap-up sweep, not in the moment. See
  `documentation/bugs/claude/2026-07-18-promised-a-follow-up-mid-conversation-without-tracking-it-as-a-todo.md`.
  A promise that only exists as text is invisible to any later
  self-check; a tracked item survives interruptions.
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
  [tools/doc_metrics](documentation/tooling/DOC_METRICS.md) (`log.py` after
  committing, `report.py` to see the trend) rather than ad hoc `wc`
  calls, so every session's numbers use the same method and stay
  comparable to each other.
- **Log the real token/dollar cost of every commit** — run
  [tools/commit_cost](documentation/tooling/COMMIT_COST.md)'s `log.py` after
  committing (same discipline as `doc_metrics` above), commit the
  resulting `commit_costs.jsonl` update. This reads actual billed usage
  from Claude Code's own session transcripts, not an estimate — see that
  tool's README for what it can and can't tell you (e.g. human-authored
  commits log a real `0`, not "unknown").
- **Commit continuously, and push after every commit**: commit coherent
  chunks of work as you go, not one giant commit at the end of a session,
  and push each one to the current branch's remote right after
  committing. This is standing authorization to commit *and push*
  without asking first (changed 2026-07-17, explicit instruction — this
  project previously followed the global CLAUDE.md default of push being
  hand-over-only; this project's own file now overrides that for plain
  pushes to the current branch specifically). Still does NOT cover
  force-push, history rewrites, pushing to a *different* branch than the
  one already checked out, or any other high-blast-radius action (defined
  below) — those are never run directly, only ever handed over as a
  copyable command for Joakim to run himself.
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
- **Bug/incident files start at investigation-open, not fix-time.** The
  moment something's being diagnosed (a live outage, a bug worth more
  than a one-line fix), create its file immediately via
  `tools/new_bug_report/new_bug_report.sh` and update it as findings come
  in, not just once it's solved. A session cut off mid-investigation must
  still leave a trail the next session can pick up from — this is the
  self-sufficiency rule applied *during* work, not only at wrap-up.
  Decided 2026-07-18 after a live server-outage investigation. Browse
  `documentation/bugs/reports/` directly (each file opens with a
  `Status:` line) — no index is kept; one was tried and removed
  2026-07-17/18 for drifting out of sync repeatedly.
- **Every bug (`documentation/bugs/reports/`) and every AI-session
  process lapse (`documentation/bugs/claude/`) is its own file — never a
  bullet appended to a shared list.** `TODO.md`/`LOG.md` in those folders
  are indexes only (one line + link each). Use
  `tools/new_bug_report/new_bug_report.sh` (add `--claude` for a process
  lapse) to create one with a consistent name and template — don't
  hand-name these. Decided 2026-07-17 after the untriaged list started
  accumulating full write-ups inline instead of staying scannable.
- **Wrap-up must verify, not just assume, that on-the-way routines
  actually ran** — decided 2026-07-17 after 3 commits went out mid-session
  without their required `doc_metrics`/`commit_cost` logging, unnoticed
  until asked about directly. At session end (and whenever picking a
  session back up), run `tools/commit_cost/check_coverage.sh` — it
  compares every commit in `git log` against `commit_costs.jsonl` and
  reports any gap. A missing entry means the logging step was skipped for
  that commit; catch up before considering wrap-up done. (The very last
  commit will always show as "missing" until the *next* logging run —
  that's expected, not a gap.)

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

## Known, accepted permission popups

Distinct from the hand-over-only list above — not a blast-radius call,
just commands that hit Claude Code's own hardcoded floor for `docker
run`/`rmi`/`volume rm`: it always prompts, regardless of any `Bash(*)`/
allow-list setting (confirmed 2026-07-17, see CHANGELOG — no setting can
suppress it). Attempt these directly rather than routing around them;
Joakim approves the popup live when it appears.

- `server/scripts/test_db.sh up` / `test_redis.sh up` — both call
  `docker run` internally to start disposable test fixtures.

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
- **All documentation lives under `documentation/` — no exceptions
  beyond the two above.** Code directories (`server/`, `tools/*/`) get at
  most a one-line stub `README.md` pointing into `documentation/`, never
  their own real content — the actual doc goes in the matching topic
  folder (e.g. `server/`'s toolchain notes live in
  `documentation/photo-server/TOOLCHAIN.md`) or, for project-wide
  utilities not tied to one topic, under
  [documentation/tooling/](documentation/tooling/README.md). Decided
  2026-07-16 after `server/README.md` and two `tools/*/README.md`s had
  drifted into real content living outside `documentation/` — moved and
  replaced with stubs.
