# commit_cost

Moved here from `tools/commit_cost/README.md`, per [CLAUDE.md](../../CLAUDE.md)'s documentation-layout rule — all documentation lives under `documentation/`, including tooling notes. The code itself stays at `tools/commit_cost/`.

**Purpose:** the real cost of each commit, in actual billed tokens and dollars — not an estimate derived from file size. [DOC_METRICS.md](DOC_METRICS.md) tracks documentation *size*; this tracks what it *cost to produce a given commit*, which are unrelated things — a one-line fix can cost thousands of tokens in back-and-forth, and a large generated file can cost almost nothing.

## How it works

Claude Code writes a full transcript per session as JSONL under `~/.claude/projects/<slug>/<session-uuid>.jsonl`. Every assistant turn's `message.usage` field carries the *actual billed* token counts (`input_tokens`, `output_tokens`, `cache_creation_input_tokens` split into 5m/1h TTL, `cache_read_input_tokens`) plus which `model` ran — not an estimate of anything.

`tools/commit_cost/log.py` finds the exact point each `git commit` was authored (the Bash tool call's paired `tool_result` contains the real commit hash, e.g. `[master 1733b2d] ...`), then sums every assistant turn's usage between one commit boundary and the previous one. That segment — not the whole session — is that commit's cost. A session's own `sessionId` field (present on every transcript row) is captured at the boundary row too, so `report.py --by-session` can show "what did this run produce" as well as "what did this commit cost".

## Human vs. LLM cost, honestly

A commit with no matching transcript boundary at all (a human ran `git commit` directly, no Claude Code session touched it) is logged as a **real `0`** — `cost_usd: 0.0`, every token field `0`, `llm_session_found: false` — never a null. This is deliberate: a null would be excluded from sums/sorts as "no data", which would make human-vs-LLM cost comparisons meaningless. A human commit's LLM token cost genuinely is zero.

`cost_usd` is `null` only in the one case where real tokens *were* spent but can't be honestly priced — a commit whose segment mixed more than one model (rare), or a model not in `PRICING` (log.py) yet. `total_billed_tokens` stays populated even then; only the dollar figure is withheld, rather than guessed by blending two models' prices under one.

## Pricing

Raw components (`input_tokens`, `output_tokens`, per-TTL cache-creation, cache-read) plus which `model` ran are stored per commit — not just a blended dollar figure — specifically so cost can be recomputed later if `log.py`'s `PRICING` table goes stale. Cache multipliers are fixed ratios per Anthropic's own pricing model (5m write = 1.25× input, 1h write = 2× input, read = 0.1× input); only `input_per_mtok`/`output_per_mtok` vary by model and change over time, tracked via `PRICING_SNAPSHOT_DATE`. A row's `cost_usd` was computed under whatever `PRICING_SNAPSHOT_DATE` it carries — re-running `log.py` never retroactively re-prices already-logged rows.

## Known edge cases (documented, not hidden)

- **Two `git commit` calls in one assistant turn** (hasn't happened in practice): that turn's entire usage attributes to the *first* commit; the second gets a real, correct `0` for that turn (no double-counting), though earlier turns since the prior boundary still count once, toward the first commit only.
- **`<synthetic>` model rows**: Claude Code inserts zero-usage rows with `model: "<synthetic>"` after compaction. These are excluded from a commit's `models` list entirely (never counted as "a second model") — otherwise a genuinely single-model commit would incorrectly get priced as unresolvable-mixed-model. Caught via a real compacted transcript during this tool's own development; regression-tested.
- **Subagent (sidechain) turns** carry their own real `usage` and are included in the sum — real spend attributable to the same commit, whichever session/thread produced it.
- **The `~/.claude/projects/<slug>/` directory-naming convention is undocumented, inferred empirically** (repo's absolute path with `/` replaced by `-`). If Claude Code changes this convention, `log.py`'s default transcript-directory lookup breaks silently (finds nothing, reports 100% human-only) — override with `--transcripts-dir` if that ever happens.
- **A commit resolved via a transcript file that no longer exists** (past the `cleanupPeriodDays` retention window) is indistinguishable from a genuine human-only commit — both log as a real `0`. This is a real historical-accuracy gap for very old commits, not something this tool can detect or flag differently.

## Privacy

Transcripts contain full conversation text — far more than this tool needs. Only `message.usage`, `message.model`, `sessionId`, and the specific Bash `git commit` tool_use/tool_result pairs are ever read. `commit_costs.jsonl` (git-tracked) never contains conversation prose — only commit hashes, numeric token/cost fields, model names, and session UUIDs.

## Running it

```
python3 -m unittest tools.commit_cost.test_metrics -v   # tests
python3 tools/commit_cost/log.py                         # scan, write new commits found
python3 tools/commit_cost/report.py                       # per-commit trend
python3 tools/commit_cost/report.py --by-session          # summed per session
tools/commit_cost/check_coverage.sh                       # flag commits with no logged cost row
```

`check_coverage.sh` cross-checks `git log` against `commit_costs.jsonl` and lists any commit with no logged row at all (as opposed to a real, correctly-logged `0` for a human-authored commit — see above). Run it as part of session wrap-up. Its one expected "missing" entry is always the commit just made in the current session (not logged yet because logging happens after committing) — not a real gap.
