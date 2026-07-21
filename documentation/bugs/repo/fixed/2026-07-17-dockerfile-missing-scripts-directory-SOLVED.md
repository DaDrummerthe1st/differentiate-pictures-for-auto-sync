# server/Dockerfile never copies scripts/ into the image

Status: **solved 2026-07-18** — real fix built, workaround no longer needed.

## Symptom

Found 2026-07-17, live during the P0 deploy: `docker compose exec auth python -m scripts.create_account ...` fails with `ModuleNotFoundError: No module named 'scripts'`.

## Root cause

The Dockerfile only `COPY`s `app/`, never `scripts/`, so the CLI account-creation tool documented in `documentation/photo-server/DEPLOYMENT.md` doesn't actually exist inside the running container.

## Fix applied (workaround, not the real fix)

Worked around live via an inline `python -c` one-liner calling `app.accounts.create_account` directly (bypasses the script, uses only what's already in the image). This workaround is now documented as the actual required step in `photo-server/DEPLOYMENT.md`'s step 5.

## Real fix

Added `COPY scripts/ /app/scripts/` to both the builder and final stages of `server/Dockerfile`. Test-driven: `tests/test_dockerfile_build.py` (new `@pytest.mark.docker` integration test, excluded from the default `uv run pytest tests` run - see `documentation/photo-server/TOOLCHAIN.md`'s new "Testing server/Dockerfile changes" section) builds the real image and execs `python -c "import scripts.create_account"` inside it, asserting success. Confirmed failing (`ModuleNotFoundError`) before the fix, passing after. `DEPLOYMENT.md` step 5's workaround is removed - `python -m scripts.create_account` is the documented command again.
