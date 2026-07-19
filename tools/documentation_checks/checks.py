"""Pure logic for the mechanical checks in documentation/tooling/CLEANING.md's
methodology — the subset that's actually automatable (dead links, structural
convention compliance). Cross-checking claims against code and judging
redundancy still need a real read, per that file; this only covers what a
script can verify without understanding the content.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


@dataclass(frozen=True)
class BrokenLink:
    source_file: Path
    target: str
    resolved: Path


def _tracked_md_files(root: Path) -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True
    ).stdout
    return [root / line for line in out.splitlines() if line.endswith(".md")]


def find_broken_links(root: Path) -> list[BrokenLink]:
    """Every relative markdown link in a git-tracked *.md file must resolve
    to a real file. http(s)/mailto links and pure same-file anchors are
    skipped — this only checks links to other files.
    """
    broken: list[BrokenLink] = []
    for md in _tracked_md_files(root):
        text = md.read_text(encoding="utf-8", errors="replace")
        for _label, target in _LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (md.parent / path_part).resolve()
            if not resolved.exists():
                broken.append(BrokenLink(md, target, resolved))
    return broken


def find_topic_folders_missing_todo(root: Path, exempt: frozenset[str]) -> list[Path]:
    """Per CLAUDE.md's "Documentation layout" rule: any documentation/
    subfolder that has its own README.md (i.e. is a real topic, not just a
    stray directory) must also have a TODO.md, unless it's in `exempt` —
    a pure-reference or pure-archive folder with no open-work backlog of
    its own (e.g. policies/, bugs/solved/, bugs/claude/). That distinction
    is a judgment call this function can't make on its own — the caller
    supplies it.
    """
    doc_root = root / "documentation"
    if not doc_root.is_dir():
        return []
    missing: list[Path] = []
    for child in sorted(p for p in doc_root.rglob("*") if p.is_dir()):
        rel = child.relative_to(doc_root).as_posix()
        if rel in exempt:
            continue
        if not (child / "README.md").exists():
            continue
        if not (child / "TODO.md").exists():
            missing.append(child)
    return missing


def find_non_stub_code_readmes(
    root: Path, code_dirs: list[str], max_chars: int
) -> list[Path]:
    """Per CLAUDE.md: code directories get at most a one-line stub
    README.md pointing into documentation/, never real content. A README
    over `max_chars` is a signal (not proof) that real content crept back
    in — this is a size heuristic, not a semantic check.
    """
    flagged: list[Path] = []
    for d in code_dirs:
        readme = root / d / "README.md"
        if readme.exists() and len(readme.read_text(encoding="utf-8")) > max_chars:
            flagged.append(readme)
    return flagged
