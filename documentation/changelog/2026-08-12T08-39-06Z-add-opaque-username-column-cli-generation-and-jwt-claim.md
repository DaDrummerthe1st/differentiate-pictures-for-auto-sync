# Add opaque username column, CLI generation, and JWT claim

First increment of `documentation/plans/deep-singing-firefly.md` (per-user private photo storage):
`users` gains a `username` column, an opaque random token (not a real name/email — clarified with
Joakim mid-session, see `documentation/GLOSSARY.md`'s new "Opaque token" entry) used later for
`dpfas_media/<username>/` folder scoping. `create_account` generates it automatically (no
`--username` flag — a human-chosen value would defeat the non-guessability point); the JWT access
token now carries it as a claim alongside `role`, re-read from the DB on `/refresh` the same way.
Schema change is idempotent (`ALTER TABLE ... ADD COLUMN IF NOT EXISTS`) but `NOT NULL` only
succeeds against zero rows — prod's 2 existing accounts need clearing and recreating on next
deploy, per Joakim's own call; documented in `DEPLOYMENT.md`. TDD throughout, 58/58 tests passing.

- **Doc size**: `documentation/GLOSSARY.md` +542 chars, `documentation/photo-server/DATA_DICTIONARY.md`
  +309 chars, `documentation/photo-server/DEPLOYMENT.md` +1469 chars (total +2320).
