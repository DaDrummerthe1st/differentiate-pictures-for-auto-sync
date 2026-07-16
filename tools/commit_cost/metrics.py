"""Real, per-commit token cost — see ../../documentation/tooling/COMMIT_COST.md for methodology.

Reads Claude Code session transcripts (~/.claude/projects/<slug>/*.jsonl),
finds the exact point each git commit was authored, and sums the *actual
billed* usage (not an estimate of file size) between one commit and the
next.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

_COMMIT_HASH_RE = re.compile(r"\[\S+ ([0-9a-f]{7,40})\]")


@dataclass(frozen=True)
class UsageTotals:
    input_tokens: int
    output_tokens: int
    cache_creation_5m_tokens: int
    cache_creation_1h_tokens: int
    cache_read_tokens: int

    def add(self, other: "UsageTotals") -> "UsageTotals":
        return UsageTotals(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cache_creation_5m_tokens=self.cache_creation_5m_tokens + other.cache_creation_5m_tokens,
            cache_creation_1h_tokens=self.cache_creation_1h_tokens + other.cache_creation_1h_tokens,
            cache_read_tokens=self.cache_read_tokens + other.cache_read_tokens,
        )

    def total_billed_tokens(self) -> int:
        return (
            self.input_tokens + self.output_tokens
            + self.cache_creation_5m_tokens + self.cache_creation_1h_tokens
            + self.cache_read_tokens
        )


ZERO_USAGE = UsageTotals(0, 0, 0, 0, 0)


@dataclass(frozen=True)
class ModelPricing:
    input_per_mtok: float
    output_per_mtok: float


@dataclass(frozen=True)
class CommitBoundary:
    row_index: int
    short_hash: str
    session_id: str | None


@dataclass(frozen=True)
class CommitCost:
    short_hash: str
    usage: UsageTotals
    models: tuple[str, ...]
    session_id: str | None


def parse_usage(message: dict) -> UsageTotals | None:
    usage = message.get("usage")
    if usage is None:
        return None
    breakdown = usage.get("cache_creation")
    if breakdown is not None:
        cache_5m = breakdown.get("ephemeral_5m_input_tokens", 0)
        cache_1h = breakdown.get("ephemeral_1h_input_tokens", 0)
    else:
        # no breakdown available — ephemeral 5m is the API default TTL
        cache_5m = usage.get("cache_creation_input_tokens", 0)
        cache_1h = 0
    return UsageTotals(
        input_tokens=usage.get("input_tokens", 0),
        output_tokens=usage.get("output_tokens", 0),
        cache_creation_5m_tokens=cache_5m,
        cache_creation_1h_tokens=cache_1h,
        cache_read_tokens=usage.get("cache_read_input_tokens", 0),
    )


def _bash_git_commit_tool_use_ids(content: list) -> list[str]:
    ids = []
    for block in content:
        if (
            isinstance(block, dict)
            and block.get("type") == "tool_use"
            and block.get("name") == "Bash"
            and "git commit" in block.get("input", {}).get("command", "")
        ):
            ids.append(block["id"])
    return ids


def _tool_result_text(content: list, tool_use_id: str) -> str | None:
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_result" and block.get("tool_use_id") == tool_use_id:
            text = block.get("content")
            return text if isinstance(text, str) else None
    return None


def find_commit_boundaries(rows: list[dict]) -> list[CommitBoundary]:
    boundaries: list[CommitBoundary] = []
    for row_index, row in enumerate(rows):
        message = row.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for tool_use_id in _bash_git_commit_tool_use_ids(content):
            for later_row in rows[row_index:]:
                later_message = later_row.get("message")
                if not isinstance(later_message, dict):
                    continue
                later_content = later_message.get("content")
                if not isinstance(later_content, list):
                    continue
                text = _tool_result_text(later_content, tool_use_id)
                if text is None:
                    continue
                match = _COMMIT_HASH_RE.search(text)
                if match:
                    boundaries.append(CommitBoundary(
                        row_index=row_index, short_hash=match.group(1), session_id=row.get("sessionId"),
                    ))
                break
    return boundaries


def group_events_by_commit(rows: list[dict]) -> list[CommitCost]:
    boundaries = find_commit_boundaries(rows)
    commits: list[CommitCost] = []
    segment_start = 0
    for boundary in boundaries:
        usage = ZERO_USAGE
        models: list[str] = []
        for row in rows[segment_start:boundary.row_index + 1]:
            message = row.get("message")
            if not isinstance(message, dict):
                continue
            row_usage = parse_usage(message)
            if row_usage is None:
                continue
            usage = usage.add(row_usage)
            model = message.get("model")
            # "<synthetic>" is a harness-internal, always-zero-usage row
            # (observed after compaction) — it isn't a real model that ran,
            # so it must not block single-model pricing eligibility.
            if model and model != "<synthetic>" and model not in models:
                models.append(model)
        commits.append(CommitCost(
            short_hash=boundary.short_hash, usage=usage, models=tuple(models), session_id=boundary.session_id,
        ))
        segment_start = boundary.row_index + 1
    return commits


def compute_cost(usage: UsageTotals, model: str, pricing: dict[str, ModelPricing]) -> float:
    price = pricing[model]
    return (
        usage.input_tokens * price.input_per_mtok
        + usage.output_tokens * price.output_per_mtok
        + usage.cache_creation_5m_tokens * price.input_per_mtok * 1.25
        + usage.cache_creation_1h_tokens * price.input_per_mtok * 2.0
        + usage.cache_read_tokens * price.input_per_mtok * 0.1
    ) / 1_000_000


def iter_transcript_rows(path: Path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)
