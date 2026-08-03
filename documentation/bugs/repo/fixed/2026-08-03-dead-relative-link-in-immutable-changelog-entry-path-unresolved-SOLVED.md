# Dead relative link in immutable changelog entry, path unresolved

Status: **fixed 2026-08-03**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

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

## Resolution (2026-08-03)

Took the narrower option flagged as the risk above, not the broad one: rather than
excluding *anything* wrapped in quotes (which could hide a real broken link quoted
for an unrelated reason elsewhere in the repo), `find_broken_links` now excludes
only the exact literal pair label `"X"` / target `"path"` — the specific idiom this
repo's docs use for "See [X](path)." illustrative prose, confirmed to appear
nowhere else in the repo as a real link (`grep -rn '\[X\](path)'` across all
tracked `*.md` files found only this idiom, never a real link happening to share
that label/target). See `tools/documentation_checks/checks.py`'s
`_ILLUSTRATIVE_EXAMPLE_LABEL_AND_TARGET`.

This incidentally also fixes a second, self-referential occurrence of the same
false positive: this bug file's own line 17 (`> ... "See [X](path)." stub`, inside
a blockquote, so also outside backticks) tripped the identical gap while describing
it — `python3 tools/documentation_checks/run.py`'s "BROKEN LINKS (2)" (not 1) was
this file plus the original 2026-08-02 changelog entry.

TDD: `tools/documentation_checks/test_checks.py` gained
`test_ignores_the_x_path_illustrative_idiom_even_outside_backticks` (reproduces
this exact bug — confirmed red before the fix, green after) and
`test_still_flags_a_broken_link_merely_labeled_x` (a link genuinely labeled "X"
pointing elsewhere must still be flagged if broken — proves the exclusion stayed
narrow, not "anything labeled X"). Full suite green; `documentation_checks/run.py`
now reports clean against the real repo.

## Security analysis

This is a pure documentation-tooling regex change — `find_broken_links` only reads
git-tracked `*.md` files already in the working tree and reports gaps to a local
terminal; no user input, network access, credentials, or write path is involved.
The exclusion is a fixed, exact literal pair (`"X"`, `"path"`) checked with `==`,
not a pattern that could be widened by attacker-controlled content, and it only
ever *skips a check*, never bypasses a security gate (unlike `secrets_scan` or
`app/tests` in `.githooks/pre-commit`) — the residual risk is purely "a future doc
could coincidentally use the literal link `[X](path)` as a real, resolvable link
and have that link go unchecked," which is exactly the same class of gap that
already exists for `` `[X](path)` `` inside backticks (pre-existing, not introduced
by this fix) and was judged acceptable there for the same reason: no real file in
this repo's convention is ever named `path` with no extension. No other attack
surface or data handling touched.
