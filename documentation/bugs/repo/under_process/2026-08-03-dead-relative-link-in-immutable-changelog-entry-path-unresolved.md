# Dead relative link in immutable changelog entry, path unresolved

Status: **root cause confirmed, not fixed (deliberately deferred, out of this session's approved scope)**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

`python3 tools/documentation_checks/run.py` reports one broken link, surfaced by running the new `tools/wrapup_checklist/run.py` against this repo's real state (2026-08-03):

```
BROKEN LINKS (1):
  documentation/changelog/2026-08-02T19-13-09Z-collapse-5-stub-readmes-onto-the-shorter-one-line-convention-trim-authentication-md-policy-md-restatement.md: [path] -> /home/joakim/code/project/differentiate-pictures-for-auto-sync/documentation/changelog/path MISSING
```

## Investigation log

1. Opened the flagged file at line 3:
   > `tools/create_bug_report/README.md` and `tools/create_changelog_entry/README.md` already used a bare "See [X](path)." stub; ...
   `"See [X](path)."` is markdown-link *syntax* used as illustrative prose — describing what the stub-README convention looks like, quoting `[X](path)` as a literal example — not an actual link meant to resolve to a real file called `path`.
2. Checked `tools/documentation_checks/checks.py`'s `find_broken_links` (`checks.py:32-49`): it already has an inline-code exclusion (`_INLINE_CODE_RE`, blanking out backtick-wrapped spans before scanning for links) specifically for this "illustrative example, not a real link" case — see the comment at `checks.py:38-40`.
3. Confirmed the gap: in this changelog entry, `[X](path)` is wrapped in plain double quotes (`"See [X](path)."`), not backticks. The existing exclusion only strips backtick spans, so this quote-wrapped example slips through and gets scanned as a real link.
4. Ruled out: this is not a bug in the changelog entry's content (the prose is correct and, per this project's changelog-immutability rule, must not be edited even for a cosmetic fix) — it's a false-positive gap in `find_broken_links`'s example-detection heuristic, which only recognizes one of the two ways this repo's prose quotes illustrative markdown-link syntax (backticks, not double quotes).

## Leading theory (confirmed)

`tools/documentation_checks/checks.py`'s dead-link sweep only excludes illustrative markdown-link examples wrapped in backticks, not ones wrapped in plain double quotes (as used in the 2026-08-02 changelog entry above). The fix belongs in `find_broken_links`/`_INLINE_CODE_RE` (or a new exclusion pattern alongside it), not in the changelog file, which is correctly immutable.

## Next session should start with

Deciding whether to extend `find_broken_links`'s exclusion to quote-wrapped illustrative examples too (risk: over-broad exclusion could hide a real broken link that happens to sit inside quotes elsewhere - needs a test case either way, per this repo's TDD rule) - this file was filed during a tooling-TODO build session (`tooling-todo-investigation` branch, 2026-08-03) whose approved scope was three specific tools; fixing the scanner itself was deliberately left for a separate pass rather than expanding that scope unasked.
