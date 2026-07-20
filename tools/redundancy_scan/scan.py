"""Pure logic for surfacing markdown phrases repeated verbatim across two or
more files - the mechanized version of documentation/tooling/CLEANING.md's
manual repeated-phrase scan (first done ad hoc 2026-07-20, see that
CHANGELOG entry). A match here is only ever a candidate for a human (or AI)
reviewer to judge, never an automatic fix - template boilerplate, a
restatement kept for standalone readability, or markdown syntax itself
(table headers) can all legitimately repeat. See
../../documentation/tooling/REDUNDANCY_SCAN.md.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

_WORD_RE = re.compile(r"\w+")


@dataclass(frozen=True)
class RepeatedPhrase:
    file_a: str
    file_b: str
    phrase: str
    word_count: int


def _tokenize(text: str) -> list[str]:
    return _WORD_RE.findall(text)


def find_repeated_phrases(
    files: dict[str, str], min_words: int = 10
) -> list[RepeatedPhrase]:
    """Every pair of distinct files is compared token-by-token (case-sensitive
    - this looks for truly verbatim repetition, not paraphrase) via
    difflib.SequenceMatcher, which finds maximal contiguous matching runs
    rather than fixed-size n-gram windows - so a 30-word repeated block is
    reported once, not as a dozen overlapping 10-word matches.
    """
    names = sorted(files)
    tokens = {name: _tokenize(files[name]) for name in names}
    matches: list[RepeatedPhrase] = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            matcher = SequenceMatcher(None, tokens[a], tokens[b], autojunk=False)
            for block in matcher.get_matching_blocks():
                if block.size >= min_words:
                    phrase = " ".join(tokens[a][block.a : block.a + block.size])
                    matches.append(RepeatedPhrase(a, b, phrase, block.size))
    return matches
