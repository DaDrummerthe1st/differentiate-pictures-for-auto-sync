"""Extract exact per-commit token cost from Claude Code session transcripts.
See README.md for methodology.

Usage:
  python3 tools/commit_cost/log.py                       # scan, write new commits found
  python3 tools/commit_cost/log.py --transcripts-dir DIR  # override transcript directory
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from metrics import (  # noqa: E402
    CommitCost,
    ModelPricing,
    compute_cost,
    group_events_by_commit,
    iter_transcript_rows,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
JSONL_PATH = Path(__file__).parent / "commit_costs.jsonl"

# Fixed cache-pricing ratios per Anthropic's own model (see shared/prompt-caching.md
# in the claude-api skill): 5m cache write = 1.25x input, 1h write = 2x input,
# cache read = 0.1x input. Only input_per_mtok/output_per_mtok vary by model and date.
PRICING_SNAPSHOT_DATE = "2026-06-24"
PRICING: dict[str, ModelPricing] = {
    "claude-fable-5": ModelPricing(10.00, 50.00),
    "claude-mythos-5": ModelPricing(10.00, 50.00),
    "claude-opus-4-8": ModelPricing(5.00, 25.00),
    "claude-opus-4-7": ModelPricing(5.00, 25.00),
    "claude-opus-4-6": ModelPricing(5.00, 25.00),
    "claude-opus-4-5": ModelPricing(5.00, 25.00),
    "claude-sonnet-5": ModelPricing(3.00, 15.00),
    "claude-sonnet-4-6": ModelPricing(3.00, 15.00),
    "claude-sonnet-4-5": ModelPricing(3.00, 15.00),
    "claude-haiku-4-5": ModelPricing(1.00, 5.00),
}


def _project_slug(repo_root: Path) -> str:
    return str(repo_root).replace("/", "-")


def default_transcripts_dir(repo_root: Path) -> Path:
    return Path.home() / ".claude" / "projects" / _project_slug(repo_root)


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()


def _full_hash_for(short_hash: str) -> str | None:
    try:
        return _git("rev-parse", short_hash)
    except subprocess.CalledProcessError:
        return None


def _all_commit_hashes() -> list[str]:
    return _git("log", "--pretty=%H").splitlines()


def _already_logged_hashes() -> set[str]:
    if not JSONL_PATH.exists():
        return set()
    hashes = set()
    with JSONL_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                hashes.add(json.loads(line)["commit_hash"])
    return hashes


def _cost_for_commit(commit: CommitCost) -> float | None:
    # Blending two models' usage under one price would misattribute cost —
    # only price commits produced under a single model (the common case).
    if len(commit.models) != 1:
        return None
    model = commit.models[0]
    if model not in PRICING:
        return None
    return compute_cost(commit.usage, model, PRICING)


def collect_commit_costs(transcripts_dir: Path) -> dict[str, CommitCost]:
    found: dict[str, CommitCost] = {}
    if not transcripts_dir.exists():
        return found
    for path in sorted(transcripts_dir.glob("*.jsonl")):
        rows = list(iter_transcript_rows(path))
        for commit in group_events_by_commit(rows):
            found.setdefault(commit.short_hash, commit)
    return found


def log_new_commits(transcripts_dir: Path) -> None:
    already_logged = _already_logged_hashes()
    found_by_short_hash = collect_commit_costs(transcripts_dir)
    all_hashes = _all_commit_hashes()

    recorded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    new_rows = []
    llm_assisted = 0
    human_only = 0

    for full_hash in all_hashes:
        if full_hash in already_logged:
            continue
        commit = None
        for candidate_short, candidate in found_by_short_hash.items():
            if full_hash.startswith(candidate_short):
                commit = candidate
                break

        if commit is None:
            # No Claude Code session touched this commit at all — the true,
            # known LLM token cost is zero, not "unknown". This is what makes
            # human-vs-LLM cost comparisons meaningful: a human-only commit
            # is a real 0, never a null that would otherwise be excluded
            # from a sum or sort as "no data".
            new_rows.append({
                "commit_hash": full_hash,
                "recorded_at": recorded_at,
                "task": None,
                "session_id": None,
                "models": [],
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_creation_5m_tokens": 0,
                "cache_creation_1h_tokens": 0,
                "cache_read_tokens": 0,
                "total_billed_tokens": 0,
                "cost_usd": 0.0,
                "pricing_snapshot_date": None,
                "llm_session_found": False,
            })
            human_only += 1
            continue

        # A session did produce this commit, so real tokens were spent —
        # cost_usd is null only when that real spend can't be honestly
        # priced (mixed/unrecognized model), never when there's simply no
        # session (that case is handled above, as a true 0).
        cost = _cost_for_commit(commit)
        new_rows.append({
            "commit_hash": full_hash,
            "recorded_at": recorded_at,
            "task": None,
            "session_id": commit.session_id,
            "models": list(commit.models),
            "input_tokens": commit.usage.input_tokens,
            "output_tokens": commit.usage.output_tokens,
            "cache_creation_5m_tokens": commit.usage.cache_creation_5m_tokens,
            "cache_creation_1h_tokens": commit.usage.cache_creation_1h_tokens,
            "cache_read_tokens": commit.usage.cache_read_tokens,
            "total_billed_tokens": commit.usage.total_billed_tokens(),
            "cost_usd": cost,
            "pricing_snapshot_date": PRICING_SNAPSHOT_DATE if cost is not None else None,
            "llm_session_found": True,
        })
        llm_assisted += 1

    if new_rows:
        with JSONL_PATH.open("a", encoding="utf-8") as fh:
            for row in new_rows:
                fh.write(json.dumps(row) + "\n")

    print(f"Logged {llm_assisted} LLM-assisted commit(s), {human_only} human-only (0 tokens, real not unknown).")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcripts-dir", type=Path, default=None)
    args = parser.parse_args()
    transcripts_dir = args.transcripts_dir or default_transcripts_dir(REPO_ROOT)
    log_new_commits(transcripts_dir)


if __name__ == "__main__":
    main()
