# redundancy_scan

**Purpose:** mechanizes the "find phrases repeated verbatim across files" step of a [CLEANING.md](CLEANING.md) pass. First done ad hoc 2026-07-20 (see that CHANGELOG entry: a manual scan at 12-word and 10-word windows, reviewed by hand) — built as a real tool 2026-07-20 so it isn't hand-rolled again, same reasoning that already justified [DOC_METRICS.md](DOC_METRICS.md)/[DOCUMENTATION_CHECKS.md](DOCUMENTATION_CHECKS.md) existing.

**What it does NOT replace**: it only finds *verbatim* repetition — same words, same order, same case. It says nothing about whether a match should be cut (see CLEANING.md's ordering: check whether a cross-reference could replace it, before deciding to delete/merge), and it can't find *paraphrased* redundancy (the same fact stated in different words) at all — that still needs a real read.

## How it works

Every pair of git-tracked `*.md` files (excluding `CHANGELOG.md` — see below) is tokenized into words and compared via `difflib.SequenceMatcher`, which finds maximal contiguous matching runs rather than fixed-size n-gram windows. A 30-word repeated block is reported once, not as a dozen overlapping 10-word windows — the main advantage over the original ad hoc approach. Matching is case-sensitive by design: this tool looks for truly verbatim text, not paraphrase, so a capitalization difference at a sentence boundary is treated as a real (if minor) difference, not noise to collapse away.

`CHANGELOG.md` is always excluded: it's append-only and its dated entries share template boilerplate by design (per CLEANING.md) — including it would drown real candidates in expected repetition.

## Every match is a candidate, never an automatic fix

Unlike [documentation_checks](DOCUMENTATION_CHECKS.md)'s dead-link/missing-`TODO.md` checks (unambiguous violations), a repeated phrase is not automatically wrong. Precedent from the 2026-07-20 pass, reviewed and deliberately left alone:

- Markdown syntax itself (table header rows) matching across files — not content.
- Templated boilerplate that's the *current*, intentional output of a generator script (e.g. `create_bug_report.sh`'s report template) — appearing in every file it generated, not stale duplication.
- A restatement kept so a file can stand alone (e.g. two `README.md` stub files sharing the same one-line "moved to documentation/" sentence — a reader landing on either directly still needs the pointer).
- CLAUDE.md rule text quoted inside a `bugs/claude-bugs/` incident report documenting a violation of that exact rule — citing the rule you broke is the point of an incident report, not duplication to cut.

Run `run.py` first to generate candidates, then judge each one by CLEANING.md's ordering (cross-reference first, then compaction) — never delete/merge on the tool's output alone.

## Running it

```
python3 -m unittest tools.redundancy_scan.test_scan -v   # tests
python3 tools/redundancy_scan/run.py                      # scan at the default 10-word threshold
python3 tools/redundancy_scan/run.py --min-words 15       # raise the threshold to cut noise
```

Always exits 0 — it surfaces, it doesn't fail a build.
