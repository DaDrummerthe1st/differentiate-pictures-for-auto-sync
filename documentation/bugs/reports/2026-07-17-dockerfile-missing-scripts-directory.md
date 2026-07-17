# server/Dockerfile never copies scripts/ into the image

Status: **worked around, real fix not built**.

## Symptom

Found 2026-07-17, live during the P0 deploy: `docker compose exec auth
python -m scripts.create_account ...` fails with `ModuleNotFoundError:
No module named 'scripts'`.

## Root cause

The Dockerfile only `COPY`s `app/`, never `scripts/`, so the CLI
account-creation tool documented in `documentation/photo-server/
DEPLOYMENT.md` doesn't actually exist inside the running container.

## Fix applied (workaround, not the real fix)

Worked around live via an inline `python -c` one-liner calling
`app.accounts.create_account` directly (bypasses the script, uses only
what's already in the image). This workaround is now documented as the
actual required step in `photo-server/DEPLOYMENT.md`'s step 5.

## Real fix, not built yet

Add `COPY scripts/ /app/scripts/` (and whatever else
`scripts/create_account.py` imports beyond `app.*`) to
`server/Dockerfile`, rebuild, and re-verify the documented command in
DEPLOYMENT.md actually works before trusting that doc again.
