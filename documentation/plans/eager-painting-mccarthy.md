# Future-proof the doc_metrics / commit_cost coverage checks

## Context

A prior session's instructions (pasted into this session) set a future-proofing
bar for `tools/doc_metrics/check_coverage.sh` and `tools/commit_cost/check_coverage.sh`:
scale sub-quadratically with repo growth, survive a jsonl schema change loudly
rather than silently, be one shared implementation instead of parallel copies,
be enforced by something other than an AI session remembering to run it, and
have a test suite that would actually catch a regression in the checker itself.

Investigating before building surfaced that a *different* session had, in the
meantime, built `tools/wrapup_checklist/` on a sibling branch (`master`),
which already reimplements roughly the same "which commits are missing a
ledger row" logic in Python — but as a *third*, additional implementation
sitting alongside the two original shell scripts, not a replacement for them.
That work has now been merged into this branch (both `master` and `curation`
are unified at the same commit). So the actual task is no longer "build a
coverage checker from scratch" — it's "make the already-built Python version
the *one* implementation, fix its remaining gaps against the bar, and wire it
in so it can't be silently skipped again."

## What's already true post-merge (verified, not assumed)

- `tools/wrapup_checklist/checks.py::missing_logged_commits(candidate_hashes, logged_hashes)`
  is already a single, ledger-agnostic, unit-tested function used for both
  `commit_cost` and `doc_metrics` coverage in `run.py`.
- `run.py` reads `git log` and each jsonl file with **one subprocess call and
  one file pass each**, not one per commit — already sub-quadratic, unlike the
  two shell scripts (each shell to `grep -q` the whole jsonl file *per commit*,
  and `doc_metrics/check_coverage.sh` additionally runs `git ls-tree` per
  commit — genuinely quadratic-ish, the failure mode the bar calls out).
- It uses `json.loads(line)[key]`, real parsing, not grepping raw JSON text.
- **Still missing** against the bar:
  1. The two old shell scripts still exist — three implementations of the same
     check now, not one.
  2. The JSON-parsing step (`_logged_hashes` in `run.py`) is untested, lives in
     the I/O layer, and isn't proven to fail loudly on a schema change (a
     renamed key would currently raise `KeyError` — probably correct — but
     nothing pins that behavior down).
  3. Nothing runs unprompted. `wrapup_checklist/run.py` is still a "run me at
     session close" convention, exactly the failure mode that caused the
     original 220-commit and 3-commit gaps.
  4. No test exercises "malformed/reshaped row fails loudly" or the
     sub-quadratic-scaling property (call-count, not just correctness).

## Plan

**1. Retire the two shell scripts; one implementation only**
Delete `tools/doc_metrics/check_coverage.sh` and `tools/commit_cost/check_coverage.sh`.
`tools/wrapup_checklist/{checks.py,run.py}` becomes the sole coverage-check
implementation for both ledgers, parameterized by ledger path/key exactly as
`missing_logged_commits` already is.

**2. Make the JSON-parsing step pure, tested, and loud-on-schema-change**
Move `_logged_hashes()` out of `run.py` into `checks.py` as
`logged_keys(lines: Iterable[str], key: str = "commit_hash") -> set[str]` —
takes raw jsonl lines in (not a path), so it's a pure function like its
siblings. Leave `json.loads(line)[key]` as direct key access (no `.get()`,
no try/except) so a renamed/missing key raises `KeyError` and a malformed
line raises `json.JSONDecodeError` — both loud, both already the natural
behavior, now pinned down by a test instead of incidental.

**3. Tests added to `tools/wrapup_checklist/test_checks.py`**
   - `logged_keys` returns the right set from well-formed lines (happy path).
   - A line missing the expected key raises `KeyError` (schema-shape-change →
     loud failure, not a silent "not logged").
   - A malformed (non-JSON) line raises `json.JSONDecodeError`.
   - Keep the two existing tests that already cover "missing commit detected"
     and "zero-`.md`-file commit excluded" — no change needed, they're correct.

   New `tools/wrapup_checklist/test_run.py` (this module currently has no
   test file — `run.py` is thin CLI glue per the project's existing
   convention, but the *scaling* property specifically lives in how it calls
   git, so it needs its own guard):
   - Mock `subprocess.run` and assert `_all_commit_hashes()` and
     `_changed_files_by_commit()` each issue exactly **one** git invocation
     — regardless of how many commits exist. This is the regression guard
     for "runtime must not grow faster than ~linear with commit count": if a
     future edit reintroduces a per-commit git call (the old shell scripts'
     pattern), this test fails immediately instead of only showing up as a
     slowdown at 10x scale.

**4. Wire coverage into `.githooks/pre-commit`, blocking, after the existing
   `app/tests` and `secrets_scan` gates**
Add a `--coverage-only` flag to `run.py` that runs just the two ledger
coverage checks (skips `documentation_checks`'s dead-link sweep and the
judgment-call reminders — those stay session-close-only, not commit-time,
since they're either slow across the whole doc tree or genuinely need
session-scoped judgment). Pre-commit runs
`python3 tools/wrapup_checklist/run.py --coverage-only` and blocks the commit
if either ledger has a gap.

Why this actually closes the gap and isn't circular: `.githooks/pre-commit`
runs *before* the new commit object exists, so `git log` at that point still
ends at the *previous* commit — which, if wrap-up conventions were followed,
should already be logged. So this catches a gap at the very next commit
attempt, not just whenever a session remembers to run the full checklist —
directly targeting the "a step quietly stopped happening and nothing noticed
for weeks" failure mode. No special-casing for "current HEAD not logged yet"
is needed here (unlike `run.py`'s session-close mode), since the commit being
created doesn't exist yet at hook time.

**5. Docs**
   - `DOC_METRICS.md` / `COMMIT_COST.md`: remove the `check_coverage.sh` line
     from "Running it", replace with a pointer to
     `tools/wrapup_checklist/run.py` (full, for session close) and note the
     `--coverage-only` mode now runs automatically pre-commit.
   - `WRAPUP_CHECKLIST.md`: add a short "Scaling" section stating the
     complexity argument plainly (one git call + one file pass per ledger,
     independent of history length) and pointing at the new call-count test
     as the regression guard — this is reasoned-about, not live-benchmarked
     at 10x; said explicitly rather than implied.
   - `README.md`'s wrap-up table: note the coverage row is now pre-commit
     enforced, not just session-close, mirroring how the secrets-scan row
     already documents its own enforcement.
   - **Not touched**: `CHANGELOG_ARCHIVE.md`, anything under
     `documentation/bugs/*/fixed/`, and past `documentation/changelog/*.md`
     entries that mention `check_coverage.sh` by name — those are the
     historical record of what existed *at the time*; per this repo's own
     changelog-immutability convention they stay as-is even though the file
     they name no longer exists.

## Explicit tradeoff (per the future-proofing bar's own instruction to name
what doesn't clear it)

The 10x-scale claim is **reasoned, not measured** — there's no 10x-sized copy
of this repo to benchmark against. The mitigation is architectural (single
git call + single file pass, independent of `N`) plus a test that pins the
call-count invariant so a regression is caught immediately rather than only
showing up as a slowdown later. This is weaker than an actual measured
benchmark at scale, called out explicitly rather than presented as proven.

## Verification
- `python3 -m unittest tools.wrapup_checklist.test_checks tools.wrapup_checklist.test_run -v`
- `python3 tools/wrapup_checklist/run.py --coverage-only` — should print clean
  against this repo's real, already-consistent ledgers.
- Make a throwaway doc-only commit locally to confirm the pre-commit hook's
  new gate fires (and doesn't false-positive on the commit being created).
- Full existing suites still green: `python3 -m pytest app/tests -q` and
  `python3 -m unittest discover -s tools -p "test_*.py"`.
- Confirm neither `tools/doc_metrics/check_coverage.sh` nor
  `tools/commit_cost/check_coverage.sh` is referenced anywhere except
  immutable historical docs (`grep -rn check_coverage.sh` excluding
  `CHANGELOG_ARCHIVE.md` / `bugs/*/fixed/` / `changelog/*.md`).
