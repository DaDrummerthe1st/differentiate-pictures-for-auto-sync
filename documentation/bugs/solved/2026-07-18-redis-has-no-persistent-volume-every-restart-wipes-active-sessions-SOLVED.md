# Redis has no persistent volume - every restart wipes active sessions

Status: **fixed, 2026-07-20**. `docker-compose.prod.yml`'s `redis` service now mounts a named `redis_data` volume at `/data` and runs with `--appendonly yes`, so refresh tokens (and their TTLs) survive a container restart.

## Fix applied, 2026-07-20

Added `redis_data:/data` to the `redis` service's `volumes:` and `--appendonly yes` to its `command:` in `docker-compose.prod.yml`, plus the matching top-level `redis_data:` volume declaration - same shape as `postgres_data`. Verified locally with a disposable `redis:8.8-alpine` container (same image/version, same flags, its own throwaway volume - not the real prod stack): set a key with `EX 3600`, restarted the container, confirmed the key and its remaining TTL were both intact afterward. Not yet verified against the actual production stack (that restart is a live, user-facing action - hand this off to Joakim to redeploy and confirm a real logged-in session survives a `docker compose restart redis` before fully trusting it end-to-end).

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
