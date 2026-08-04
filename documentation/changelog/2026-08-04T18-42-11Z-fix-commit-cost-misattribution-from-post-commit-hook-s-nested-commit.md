# Fix commit_cost misattribution from post-commit hook's nested commit

Two bugs found live: log.py invoked from inside its own triggering commit's Bash call can't see that commit's transcript boundary yet (`--exclude-current-head` defers it); the nested auto-log commit's confirmation line prints before the outer one, so the old first-match regex grabbed the wrong hash (now takes the last match). Corrected the one resulting bad row (`18f8b64`: was `$0`, is really `$12.01`).

- **Doc size**: +7,236 chars (`COMMIT_COST.md` + bug report).
