# doc_metrics

Moved here from `tools/doc_metrics/README.md`, per [CLAUDE.md](../../CLAUDE.md)'s documentation-layout rule. Code stays at `tools/doc_metrics/`.

**Purpose:** a durable ledger of what each iteration of work cost in documentation, and what it paid for — not just a char-count trend line. Every logged commit answers three questions at once: how much did the repo's docs grow or shrink, in service of which TODO item or outcome (`task`, see below), and — the mechanical baseline this was originally built for — measured the same consistent way every time, instead of manually eyeballed with `wc -c` (which counts bytes, not characters, and diverges from a true count once em dashes or other multi-byte characters are involved). The character-count-change rule this serves lives in [CLAUDE.md](../../CLAUDE.md). For what a commit *cost* (real billed tokens/dollars) rather than what it *produced* in doc size, see [COMMIT_COST.md](COMMIT_COST.md) — a different axis, not a duplicate of this tool.

## Methodology (fixed, for comparability)

- **Character count = Unicode codepoints** — `len()` of the UTF-8-decoded text, not `wc -c` (bytes) and not `wc -m` (locale-dependent). This is a deliberate correction: this session's earlier changelog entries used `wc -c` byte counts, which run ~0.8% high on this repo's docs due to em dashes. Going forward, all entries use this script's codepoint count — treat the switchover as a one-time methodology note, not a regression.
- **Scope = every `*.md` file *tracked by git*** — `git ls-files`, not a filesystem walk. This is a deliberate correction too: `discover_md_files` used to be `root.rglob("*.md")`, which silently picked up vendored `*.md` files inside gitignored directories (`server/.venv/`'s package license files, a bundled FastAPI agent-skill doc) — text that isn't this repo's documentation and varies by whatever happens to be installed locally, which broke the "every snapshot scoped identically" goal below. Fixed at commit-time of this note; historical `metrics.jsonl` rows logged before the fix (all under `log_current_commit`, never `--backfill`, which already used `git ls-tree` and was unaffected) still contain that pollution — same precedent as the codepoint-vs-`wc -c` switch above, left as-is rather than rewritten, since the jsonl is append-only. ~21.6% of all summed characters logged to date (427,518 of 1,974,536) came from this bug.
- **Granularity = one row per file per commit.** Folder- or repo-level totals (e.g. what changelog entries report) are always a `SUM()` over these rows, never stored separately — one source of truth, no risk of the aggregate drifting from the detail.
- **Task linkage, optional.** Every row can carry a `task` label (e.g. `"photo-server 0.3"`) via `log.py --task "..."`, answering not just *how much* documentation grew but *what it paid for* — which TODO item or outcome the growth served. Rows logged without `--task` have no `task` key at all (not just `null`) — code reading `metrics.jsonl` directly must use `.get("task")`, never `["task"]`.
- **jsonl keys = sqlite column names, exactly.** Renamed for readability (`ts`→`recorded_at`, `commit`→`commit_hash`, `file`→`file_path`, `chars`→`char_count`; `branch`/`task` were already clear) and so the two representations of the same data never drift into different vocabularies. Applied retroactively to all existing rows — a pure key-rename, no values touched — as a value-preserving exception to "jsonl is append-only": renaming a key's spelling isn't rewriting a past *entry*'s meaning the way editing a changelog entry would be.

## Files

- `tools/doc_metrics/metrics.py` — pure logic (counting, snapshotting, persistence). Tested in `test_metrics.py`.
- `tools/doc_metrics/log.py` — CLI. Run with no args after a commit to snapshot HEAD. `--backfill` walks the full commit history via `git show`/`git ls-tree` (read-only — never checks out a commit or touches the working tree) and snapshots every commit that already exists, so the trend doesn't start empty.
- `tools/doc_metrics/report.py` — CLI. Prints char count, delta from the previous logged commit, and an estimated token count per commit, plus the `task` label if that commit was tagged with one. `--by-task` instead prints total char/token cost grouped by `task` label — sorted by most expensive first — to answer "how much did TODO item X cost in documentation."
- `tools/doc_metrics/metrics.jsonl` — append-only, **git-tracked**. One JSON line per (commit, file). This is the durable record — per CLAUDE.md's self-sufficiency rule, the data has to live in the repo, not only in a local database.
- `tools/doc_metrics/metrics.db` — SQLite, **gitignored**. Kept in sync from the same `persist_snapshot()` calls that write the jsonl; exists purely so `report.py` can run SQL aggregates instead of re-parsing the jsonl every time. If it's ever deleted (or a fresh clone doesn't have it yet), run `python3 tools/doc_metrics/log.py --rebuild-db` to regenerate it from `metrics.jsonl`.

## "Token cost" — what this can and can't tell you

`report.py` divides characters by 4 as a rough tokens-per-character approximation. That ratio is a common rule of thumb, not measured against this repo's actual tokenizer — treat the `~tokens` column as directional (is it growing, by roughly how much), not a precise or billable figure. Actual API cost additionally depends on current per-model pricing, which isn't tracked here because it changes independently of anything in this repo. For an *exact* per-commit token count and dollar cost, see [COMMIT_COST.md](COMMIT_COST.md) instead.

## One-commit lag (expected, not a bug)

`log.py` records the *current* HEAD, so it can only be run after a commit exists — a commit's own snapshot always lands in the jsonl update that gets committed next, one commit behind. This project never amends commits (see CLAUDE.md), so there's no way to close that gap; it's a permanent, harmless one-line-per-commit lag, not something to chase.

## Running it

```
python3 -m unittest tools.doc_metrics.test_metrics -v   # tests
python3 tools/doc_metrics/log.py --backfill              # one-time, history to date
python3 tools/doc_metrics/log.py                         # after each commit touching *.md
python3 tools/doc_metrics/log.py --task "photo-server 0.3"  # ...tagged with the task it served
python3 tools/doc_metrics/report.py                       # see the trend
python3 tools/doc_metrics/report.py --by-task             # see cost grouped by task
```
