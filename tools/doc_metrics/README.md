# doc_metrics

Tracks `*.md` character counts over time, per file, tied to git commits —
so the character-count-change rule in [CLAUDE.md](../../CLAUDE.md) is
measured the same way every time instead of manually eyeballed with
`wc -c` (which counts bytes, not characters, and diverges from a true
count once em dashes or other multi-byte characters are involved).

## Methodology (fixed, for comparability)

- **Character count = Unicode codepoints** — `len()` of the UTF-8-decoded
  text, not `wc -c` (bytes) and not `wc -m` (locale-dependent). This is
  a deliberate correction: this session's earlier changelog entries used
  `wc -c` byte counts, which run ~0.8% high on this repo's docs due to
  em dashes. Going forward, all entries use this script's codepoint
  count — treat the switchover as a one-time methodology note, not a
  regression.
- **Scope = every `*.md` file in the repo**, found recursively from the
  repo root. Not configurable per run, so every snapshot is scoped
  identically — that's what makes commits comparable to each other.
- **Granularity = one row per file per commit.** Folder- or repo-level
  totals (e.g. what CHANGELOG.md entries report) are always a `SUM()`
  over these rows, never stored separately — one source of truth, no
  risk of the aggregate drifting from the detail.

## Files

- `metrics.py` — pure logic (counting, snapshotting, persistence).
  Tested in `test_metrics.py`.
- `log.py` — CLI. Run with no args after a commit to snapshot HEAD.
  `--backfill` walks the full commit history via `git show`/`git ls-tree`
  (read-only — never checks out a commit or touches the working tree)
  and snapshots every commit that already exists, so the trend doesn't
  start empty.
- `report.py` — CLI. Prints char count, delta from the previous logged
  commit, and an estimated token count per commit.
- `metrics.jsonl` — append-only, **git-tracked**. One JSON line per
  (commit, file). This is the durable record — per CLAUDE.md's
  self-sufficiency rule, the data has to live in the repo, not only in a
  local database.
- `metrics.db` — SQLite, **gitignored**. Kept in sync from the same
  `persist_snapshot()` calls that write the jsonl; exists purely so
  `report.py` can run SQL aggregates instead of re-parsing the jsonl
  every time. If it's ever deleted (or a fresh clone doesn't have it
  yet), run `python3 tools/doc_metrics/log.py --rebuild-db` to
  regenerate it from `metrics.jsonl`.

## "Token cost" — what this can and can't tell you

`report.py` divides characters by 4 as a rough tokens-per-character
approximation. That ratio is a common rule of thumb, not measured
against this repo's actual tokenizer — treat the `~tokens` column as
directional (is it growing, by roughly how much), not a precise or
billable figure. Actual API cost additionally depends on current
per-model pricing, which isn't tracked here because it changes
independently of anything in this repo.

## One-commit lag (expected, not a bug)

`log.py` records the *current* HEAD, so it can only be run after a
commit exists — a commit's own snapshot always lands in the jsonl update
that gets committed next, one commit behind. This project never amends
commits (see CLAUDE.md), so there's no way to close that gap; it's a
permanent, harmless one-line-per-commit lag, not something to chase.

## Running it

```
python3 -m unittest tools.doc_metrics.test_metrics -v   # tests
python3 tools/doc_metrics/log.py --backfill              # one-time, history to date
python3 tools/doc_metrics/log.py                         # after each commit touching *.md
python3 tools/doc_metrics/report.py                       # see the trend
```
