# documentation_checks

**Purpose:** the mechanical subset of [CLEANING.md](CLEANING.md)'s
audit methodology, as a real script instead of being rewritten ad hoc
every time a cleaning pass runs. Built 2026-07-19, after the second
cleaning pass that day paid to regenerate a dead-link-sweep script from
scratch twice in one session — the same "structured tool instead of ad
hoc commands" reasoning that already justified
[DOC_METRICS.md](DOC_METRICS.md)/[COMMIT_COST.md](COMMIT_COST.md)
existing.

**What it does NOT replace**: CLEANING.md's own methodology has five
steps; only step 3 (dead-link sweep) and part of step 4 (structural
convention compliance) are mechanical enough to script. Reading every
doc in full, cross-checking claims against the actual code, and judging
what's redundant all still need a real read — by a person or an AI
session — not a script. Run this first to clear the mechanical ground,
then still do the real pass.

## Checks

1. **Dead-link sweep** — every relative markdown link in a git-tracked
   `*.md` file resolves to a real file. `http(s)://`/`mailto:` links and
   pure same-file anchors are skipped.
2. **Topic-folder `TODO.md` presence** — per CLAUDE.md's "Documentation
   layout" rule, any `documentation/` subfolder with its own `README.md`
   must also have a `TODO.md`, unless it's pure-reference or
   pure-archive (no backlog of its own). Which folders qualify for that
   exemption is a judgment call a script can't make alone — the
   exemption list (`policies`, `bugs/solved`, `bugs/claude`, with the
   reasoning for each) lives in `run.py`, reviewable and editable there,
   not buried in the check's logic.
3. **Code-dir stub-README size** — a soft check (warns, doesn't fail):
   flags a code-directory `README.md` longer than 400 characters as
   worth a manual look, since CLAUDE.md caps these at "at most a
   one-line stub." A size threshold can't prove content crept back in,
   only suggest it — treat a flag here as "check this file," not as an
   automatic violation.

**Not checked here** (would need semantic understanding, not string
matching): nothing project-wide duplicated outside `POLICY.md`; a "see
X" cross-reference terminating in real content rather than another
pointer; whether a fact in a doc still matches what the code actually
does.

## Running it

```
python3 -m unittest tools.documentation_checks.test_checks -v   # tests
python3 tools/documentation_checks/run.py                        # run the checks
```

Exit code `1` if a broken link or a missing topic-folder `TODO.md` was
found; `0` otherwise (a stub-size warning alone doesn't fail the run).
