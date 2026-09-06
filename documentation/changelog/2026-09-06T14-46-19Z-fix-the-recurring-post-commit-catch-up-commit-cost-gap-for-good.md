# Fix the recurring post-commit catch-up commit_cost gap for good

Hit the same commit_cost logging gap twice in one session while committing the Android app work.
Root cause: `.githooks/post-commit`'s auto-generated catch-up commit skipped logging the exact
commit it existed to catch up, every single time, due to its own recursion guard. Rather than patch
that guard a third time (it was already patched once, 2026-09-05, for a different edge case), moved
the logging into `.githooks/pre-commit` instead — self-healing, folded straight into the commit
already being made, no separate catch-up commit ever created. Deleted the now-dead
`.githooks/commit-msg` and `.githooks/catch_up_titles.sh`. Verified end-to-end via a new
`.githooks/test_commit_hooks.sh` (six commits in a row, zero gaps, zero extra commits) and against
the real repo. Also: appended `Gradle`/`Android Gradle Plugin` to the glossary, and ignored
Android Studio's project-local `android/.idea/`.

- **Doc size**: `GLOSSARY.md` +1021; `COMMIT_COST.md` +988; `DOC_METRICS.md` +415;
  `tooling/README.md` +195; `tooling/TODO.md` -563; bug report (moved to `fixed/`) +2724. Net +4780
  chars.
