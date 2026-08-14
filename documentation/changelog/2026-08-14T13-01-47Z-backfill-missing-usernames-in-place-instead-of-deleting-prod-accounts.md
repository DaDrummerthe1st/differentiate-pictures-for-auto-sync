# Backfill missing usernames in place instead of deleting prod accounts

Rebuilding `auth` to fix the upload-401 bug surfaced `ensure_schema()`'s NOT NULL migration crash-looping the whole service against prod's existing accounts. Added `backfill_missing_usernames()` + `scripts/backfill_username.py` to assign usernames in place instead of deleting/recreating accounts (the first-proposed fix, filed as a claude-bug).

- **Doc size**: GLOSSARY.md +1124, WORKFLOW.md +486, DEPLOYMENT.md +566, upload bug doc +4566, new claude-bug (fixed) 2827 chars.
