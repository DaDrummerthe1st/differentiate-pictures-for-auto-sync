# Real account password passed via scripted CLI flag and repeated in chat

See [README.md](../README.md) for what belongs here.

## What happened

While setting up the new local full-stack dev environment (2026-07-23 session), created the two real project accounts against the local auth container with:
```
docker compose exec -e CREATE_ACCOUNT_PASSWORD=<redacted> auth python -m scripts.create_account --email joakim.reuterborg@gmail.com --role admin
```
i.e. passed the real chosen password as a literal, scripted CLI-visible env-var assignment (redacted above — not repeating it here either, per this file's own "What changed" section) instead of using `create_account.py`'s own interactive password prompt — which the script's docstring explicitly recommends for exactly this reason ("never as a CLI argument, which would leak into shell history/process listings"). Then repeated that plaintext password back to Joakim in the chat transcript across two separate turns (once when asked directly, once again restating it), instead of stating it at most once or, better, having Joakim set his own password interactively.

Joakim flagged this as having "given the whole internet including yourself access to the web admin by hardcoding this password, writing it in the repo and spreading it in this chat context." Investigated before writing this report, per CLAUDE.md's "ask or search, never guess" rule — the alarming framing doesn't hold on two specific points, and this file should record the corrected facts, not the original claim, so a later reader isn't misled:
- **Never written to the repo**: `git grep` for the password string across every commit in the repo's full history returns nothing. It only ever existed as a literal CLI argument on the host shell and in this chat transcript — a real exposure vector, but a different and much narrower one than "in the repo."
- **No internet or LAN exposure**: the local stack's only host-published port is Caddy, bound explicitly to `127.0.0.1:8420` (confirmed in `docker-compose.yml`) — loopback-only, unreachable from the LAN or the internet. Postgres/redis/auth publish no host ports at all; uvicorn's own `--host 0.0.0.0` is the standard *inside-the-container* bind so Docker's internal bridge network can reach it, not a host/internet exposure. Nothing in this session forwarded a port or exposed this stack beyond the workstation it runs on.

The real, narrower lapse: the password passed through a scripted CLI invocation (shell-history and `docker inspect`-visible) and got repeated in chat unnecessarily — for a real, ongoing account a human will keep using, not a throwaway test fixture.

## Why it happened

Defaulted to a non-interactive, scripted `docker compose exec -e ...` invocation for speed/reproducibility while verifying the local stack end-to-end, without weighing that these are the two real, ongoing project accounts (`photo-server/README.md`'s "two accounts only") rather than disposable test fixtures — the convenience trade-off `create_account.py`'s docstring is warning against. Also conflated two different categories of "local-only, so it's fine to be casual about it": the local stack's fixed placeholder DB/Redis/JWT secrets (genuinely inconsequential — they protect nothing reachable from outside the host) with a real account password a human will actually keep typing, which isn't the same category of secret regardless of how local the deployment is.

## What changed

- Going forward, real account creation via `server/scripts/create_account.py` — even against a local/disposable environment — uses the interactive password prompt (or the command is handed to the human to run themselves, entering their own password), never a scripted `-e`/CLI-argument password, matching the script's own stated intent.
- A real credential is stated in chat at most once if unavoidable, never repeated across turns.
- The two local accounts' passwords should be treated as compromised (known via shell history/process listing and this chat transcript) and rotated the next time either account is touched, rather than left in place on the assumption that "local-only" made the exposure moot.
