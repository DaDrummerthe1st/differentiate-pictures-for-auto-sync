# Redis has no persistent volume - every restart wipes active sessions

Status: **fixed and verified in production, 2026-07-21**. `docker-compose.prod.yml`'s `redis` service now mounts a named `redis_data` volume at `/data` and runs with `--appendonly yes`, so refresh tokens (and their TTLs) survive a container restart.

## Fix applied, 2026-07-20

Added `redis_data:/data` to the `redis` service's `volumes:` and `--appendonly yes` to its `command:` in `docker-compose.prod.yml`, plus the matching top-level `redis_data:` volume declaration - same shape as `postgres_data`. Verified locally with a disposable `redis:8.8-alpine` container (same image/version, same flags, its own throwaway volume - not the real prod stack): set a key with `EX 3600`, restarted the container, confirmed the key and its remaining TTL were both intact afterward.

## Verified against production, 2026-07-21

Joakim redeployed (`git pull` + `docker compose -f docker-compose.prod.yml up -d redis`), confirmed `config get appendonly` returns `yes` and logs show the AOF base/incr files being created on start. Then ran the real end-to-end test: logged in at `https://photos.reuterborg.se/login`, opened an album, restarted the `redis` container (`docker compose -f docker-compose.prod.yml restart redis`), and - without reloading or re-logging in - clicked into a photo and a different album from the same still-open tab. Both loaded normally, confirming the session (and its refresh token) survived the restart. One hiccup along the way, not a bug: an `exec ... redis-cli ... ping` run immediately after `up -d redis` got "Connection refused" - just the normal gap between Compose reporting the container "Started" and `redis-server` actually finishing its boot/AOF-file creation; a moment later it answered `PONG` normally.

## Security analysis, 2026-07-21

No new attack surface: `redis` still publishes no host port (only reachable from other containers on the compose network, unchanged), and `requirepass` is untouched.

Data now written to disk (`redis_data` volume): `refresh_token:<jti> → user_id` pairs only, not the JWT itself — reading the volume alone can't forge a valid token without also having `JWT_SECRET_KEY`. Lower sensitivity than what already sits in the same trust boundary (`postgres_data` holds password hashes, `thumbcache`/`stories` hold real photos) — not a new category of at-rest risk for this deployment.

Revocation/TTL semantics preserved across a restart: `revoke_refresh_token`'s `DELETE` and the original `SET ... EX` both replay from the AOF log, so a logged-out token doesn't reappear and no TTL is extended by persisting.

**Residual risk, real but bounded — flagging to Joakim rather than treating as fully closed:** before this fix, Redis could never fail to *start* (nothing to load). Now, an unclean kill mid-write — a power loss, exactly what caused this bug in the first place — could in theory leave a truncated AOF file that Redis refuses to load until repaired with `redis-check-aof --fix`, which would turn "lose sessions" into "Redis won't start at all." Mitigated in practice: the production logs from this fix's own verification show Redis 8.8's multi-part AOF format (`appendonly.aof.1.base.rdb` + `.1.incr.aof`), which defaults to `aof-load-truncated yes` — it auto-truncates a corrupted tail and starts anyway, built specifically for this abrupt-shutdown case. So the residual window is small (at most the last `appendfsync everysec` interval) and self-healing in the common case, not eliminated. Not fixed further this session — a `redis-check-aof` health-check that alerts instead of silently crash-looping would close this properly; logging it as a follow-up rather than reopening this file as unresolved.

## Symptom

Found 2026-07-18, right after recovering from the switch-outage (`2026-07-18-photos-reuterborg-se-unreachable.md`): Joakim reported "now no new thumbnails nor pictures are loading". `docker compose -f docker-compose.prod.yml logs photo-viewer` showed a long, unbroken streak of `401 Unauthorized` on `/thumb` and `/original` requests, following a run of normal `200 OK`s - not a generation-latency problem, an auth problem.

## Investigation log

1. `docker compose -f docker-compose.prod.yml ps` showed all 5 services `Up 22 minutes` - i.e. every container had restarted together, consistent with the earlier power-loss event (the IKEA smart-plug incident that also power-cycled the switch mid-investigation of the separate outage above).
2. `docker-compose.prod.yml` reviewed: `postgres` has a named volume (`postgres_data`), but **`redis` has no `volumes:` entry at all** - pure in-memory, nothing persisted to disk.
3. Session refresh tokens are stored in Redis (`server/app/tokens.py`'s `get_redis_client`/revoke/verify path, confirmed by `auth_routes.py`'s `/refresh` route reading from there). A Redis restart with no persistence wipes every issued refresh token
   - every logged-in user's session becomes unrecoverable, even though their access-token cookie and refresh-token cookie are both still present client-side and would normally still be valid.
4. Access tokens are short-lived by design (5 minutes, `ACCESS_TOKEN_EXPIRE_MINUTES`, see CHANGELOG 07-17) specifically so they can silently renew via the refresh token without disrupting browsing - that renewal path is exactly what breaks once Redis has nothing to renew against.

## Leading theory (confirmed)

Root cause is confirmed, not just a theory: `redis`'s lack of a persistent volume in `docker-compose.prod.yml` means any container restart (crash, host reboot, `docker compose down`/`up`, or - as happened today - a wider power event) silently logs out every active session. The user only discovers this once their 5-minute access token happens to expire and the silent refresh fails, which can be well after the actual restart, making the cause non-obvious in the moment (as it was here).

## Fix, not built yet

Add a named volume for Redis's RDB/AOF persistence in `docker-compose.prod.yml` (mirroring `postgres_data`'s pattern) and configure Redis to actually use it (`--save`/`--appendonly` flags, not just mounting an unused path). Needs testing: restart the `redis` container deliberately and confirm a previously-issued refresh token still works afterward, before trusting this is fixed.

## Immediate live workaround applied

None needed beyond a fresh login - once Redis loses a session's refresh token, the only recovery is the user logging in again at `/login`, which issues a fresh token pair. Told Joakim to do this to unblock the site immediately; the underlying gap (no persistence) is what this report tracks.
