# Deployment — photo-server + photo-viewer, production stack

Everything here runs on the home server (192.168.1.10, see [HARDWARE.md](HARDWARE.md) — including its currently-overridden memtest gate, re-check that note before running anything below). Written, not run, by the AI session per [POLICY.md](../policies/POLICY.md)'s "Deployment and system access" rule — copy/paste these yourself.

## Prerequisites (must be done first)

- DNS: `photos.reuterborg.se` A record points at this network's current public IP, root domain (`reuterborg.se`) untouched — see [TODO.md](TODO.md) Phase 6's human checkpoint.
- Router: external ports 80 and 443 forwarded to 192.168.1.10.
- Both confirmed reachable from outside the LAN before starting the stack — a stack that's up but unreachable just means Let's Encrypt's HTTP-01 challenge will fail and Caddy won't get a cert.

## 1. Firewall (UFW) — written for review, not run automatically

```
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

Only these three ports. If UFW is already enabled with other rules, review before running `enable` again.

## 2. Create the .env file (repo root, on the server)

Never commit this file (`.gitignore` already excludes `/.env`). Generate real random values for the passwords — don't reuse anything.

```
cd ~/differentiate-pictures-for-auto-sync
cp .env.example .env
python3 -c "import secrets; print(secrets.token_urlsafe(32))"   # run 3x
```

Paste the three generated values into `.env` for `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, and `JWT_SECRET_KEY` (the last one must be at least 32 characters — `token_urlsafe(32)` comfortably clears that). Also set `PHOTOS_HOST_PATH` to the real photo directory on this host (confirmed 2026-07-17: `/tank/momfiles` — the ZFS pool path, not a `~/Pictures/...` guess; verify with `ls` before trusting this doc if it ever seems stale).

## 3. Bring up the stack

```
cd ~/differentiate-pictures-for-auto-sync
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps
```

Caddy will request the Let's Encrypt cert for `photos.reuterborg.se` on its first incoming request — no separate step. Watch its log if it doesn't come up clean:

```
docker compose -f docker-compose.prod.yml logs -f caddy
```

## 4. Database schema

Nothing to do here — `app/main.py`'s FastAPI `lifespan` handler calls `ensure_schema()` against the real database automatically on every `auth` container startup (idempotent `CREATE TABLE IF NOT EXISTS`, safe on every restart). Fixed 2026-07-18, see [documentation/bugs/solved/2026-07-17-postgres-schema-never-initialized-in-production-SOLVED.md](../bugs/solved/2026-07-17-postgres-schema-never-initialized-in-production-SOLVED.md).

## 5. Create the first member account

```
CREATE_ACCOUNT_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')"
docker compose -f docker-compose.prod.yml exec -e CREATE_ACCOUNT_PASSWORD="$CREATE_ACCOUNT_PASSWORD" auth python -m scripts.create_account --email elisabeth.reuterborg@gmail.com --role member
echo "Password: $CREATE_ACCOUNT_PASSWORD"
```

Replace the email/role as needed. Password is read from `CREATE_ACCOUNT_PASSWORD` (generated above so it's not typed into shell history) rather than prompted, since `docker compose exec` isn't a TTY by default here — the final `echo` is the only place it's surfaced, so it can be shared with the account holder immediately and not left sitting in shell history. Fixed 2026-07-18, see [documentation/bugs/solved/2026-07-17-dockerfile-missing-scripts-directory-SOLVED.md](../bugs/solved/2026-07-17-dockerfile-missing-scripts-directory-SOLVED.md).

Share the printed password with the account holder out of band (not over email/chat in plaintext, per [POLICY.md](../policies/POLICY.md)).

## 6. Verify

- `https://photos.reuterborg.se/login` loads, real cert (no browser warning), the login form renders.
- Log in with the account from step 5 — lands on the photo-viewer.
- Confirm a direct request to a photo/thumbnail URL without a session (e.g. `curl -i https://photos.reuterborg.se/api/tree`) returns 401.
- Single-picture and multi-picture download still work from the logged-in session (regression check — see [TODO.md](TODO.md)'s P0 note).
- **Usage-data persistence** (analytics DB, voiceover recordings survive a restart — do this concretely, not just by trusting the compose file):
  ```
  # record something (e.g. browse a photo, or record a voiceover in the UI),
  # then:
  docker compose -f docker-compose.prod.yml restart photo-viewer
  # after it's back up, confirm the data from before the restart is still there
  # (e.g. the voiceover list still shows the recording you just made)
  ```
  `thumbcache`, `analytics_data`, and `stories` are named Docker volumes (not anonymous), so this should always pass — a failure here means one of those volume declarations regressed, not that this is expected to be flaky.

## Stopping / tearing down

```
docker compose -f docker-compose.prod.yml down
```

This does **not** delete the named volumes (`postgres_data`, `analytics_data`, `stories`, `thumbcache`, `caddy_data`, `caddy_config`) — account data, usage analytics, voiceover recordings, and the Let's Encrypt cert all survive a `down` + `up`. Only `docker compose -f docker-compose.prod.yml down -v` would destroy them — never run that without knowing exactly why.

## Troubleshooting playbook

Captured 2026-07-17 from the first real P0 deploy, where several of these were worked out live under deadline pressure — reusable steps for "something's broken," roughly in the order that's cheapest-to-check first:

1. **Is this actually a server bug, or a stale browser cache?** Hard refresh (Ctrl+Shift+R) before chasing anything server-side — several "broken" symptoms during the first deploy turned out to be the browser caching failed responses from before auth/schema were fixed.
2. **Did a container restart recently without you asking it to?** `docker compose -f docker-compose.prod.yml ps` — compare "Created" vs "Up" time per service; one showing a much shorter uptime than the others (when you didn't restart it deliberately) means it crashed and `restart: unless-stopped` brought it back. Note: a deliberate `up -d --build` also resets a service's log history (new container instance) - don't mistake that for a crash on its own.
3. **Memory pressure?** `free -h` (host-level) and `docker stats --no-stream` (per-container, against each service's `mem_limit`) - this host is tight (see HARDWARE.md). Also check `dmesg 2>/dev/null | grep -i "out of memory\|oom-kill"` for a definitive OOM-kill, rather than inferring one from restarts alone.
4. **What does the service's own log say?** Filter out routine noise (uvicorn access logs, and once internet-facing, constant opportunistic bot-scanning 404s for things like `/.env`, `/config.json` - normal, ignore): `docker compose -f docker-compose.prod.yml logs <service> 2>&1
   | grep -iE "error|traceback|exception|killed"`. Grep for the specific
   endpoint/feature too (e.g. `thumb`) - zero matches for an endpoint you know was requested means the request isn't reaching that container at all, which points you at Caddy/routing/the client instead of that service's own code.
5. **Client-side evidence**: browser DevTools Network tab on the actual failing request - exact URL, status code, response body/headers. Cheap and often the fastest way to tell "client never sent it" from "server rejected it" from "server crashed handling it."
