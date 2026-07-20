# Documentation cleaning pass

A full, deliberately-invoked audit of everything under `documentation/` (plus root `README.md`/`CLAUDE.md`) — distinct from the lightweight, per-session "Doc-drift check" and "Cross-reference link check" rows in [README.md](README.md)'s wrap-up checklist, which are scoped to files a session happened to touch that day. This is a full-repo pass, invoked on demand, not automatically per session — that's deliberate: it doesn't belong in `CLAUDE.md` because it isn't something every session needs to run.

## Goals

Asked for 2026-07-19, in Joakim's own framing: reduce how long a fresh session takes to get up and running, and save tokens doing it — without losing needed context. The premise: the more thorough and precise the audit, the better-placed and better-indexed the resulting information ends up, and *that* is what actually cuts ramp-up time and tokens — not just making files shorter. A doc that's wrong or misleading costs a fresh session far more (in corrected turns) than a doc that's merely verbose costs in tokens.

## What it checks

1. **Read every doc in full**, not just grep — `documentation/**`, root `README.md`/`CLAUDE.md`. Skimming misses contradictions between two sections of the same file.
2. **Cross-check claims against actual code/config**, not just against other docs. A doc can be internally consistent and still be wrong about what the code does.
3. **Dead-link sweep** — every relative markdown link across the repo resolves to a real file. Scripted, run first: `python3 tools/documentation_checks/run.py` (see [DOCUMENTATION_CHECKS.md](DOCUMENTATION_CHECKS.md) — built 2026-07-19 after this same script got rewritten from scratch, ad hoc, twice in one session).
4. **Structural convention compliance**, per `CLAUDE.md`'s "Documentation layout" section: nothing project-wide duplicated outside `POLICY.md`; every "see X" cross-reference terminates in real content within 1-2 hops, not another pointer back; code directories stay one-line stubs; topic folders keep a `TODO.md`; root `README.md` stays the short pitch + pointer, not branch-specific content. The topic-folder-`TODO.md` and code-dir-stub-size parts are also covered by `tools/documentation_checks/run.py` above — the duplication and cross-reference-termination parts still need a real read.
5. **Fix vs. flag**: fix stale facts and structural violations directly. Flag, don't unilaterally resolve, anything that would mean editing an already-published, append-only record (e.g. a past `CHANGELOG.md` entry) — that needs Joakim's call, not a silent correction.
6. **Verify before committing**: re-run the dead-link sweep, run the full test suite, log `doc_metrics`/`commit_cost`, commit with a changelog entry detailed enough to serve as the audit's own record.

## Precedent

First run: 2026-07-19, `CHANGELOG.md`'s `(6)` entry that day and the several timestamped entries immediately after it (a changelog-heading convention fix, a `CLAUDE.md` accumulated-detail trim, and a test-rule scoping correction all surfaced *during* that pass, not planned going in — expect a cleaning pass to turn up follow-on fixes beyond the original checklist). Read that entry for what a full pass actually found in this repo, as a concrete example of scope and depth.

Practical note from that run: reading and cross-checking the whole `documentation/` tree against code is large enough to be worth spreading across a few parallel research passes by area (e.g. bugs+tooling, architecture/photo-server, policy+cross-links) rather than one linear read — keeps the pass thorough without exhausting one session's context budget before the fixes even start.
