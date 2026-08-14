# Deployment — photo-server + photo-viewer, production stack

Everything here runs on the home server (`192.168.1.10`, SSH user `joakim`, has `sudo`; commands below assume you're already connected — Joakim usually is). Hardware/OS facts for this box live in the `hardware` repo's `server/192.168.1.10/`, not here. Before any planned reboot while a memtest gate is open: `docker-compose.prod.yml`'s restart policy brings the production stack back automatically on every boot regardless of the gate's wording (it only stops a *manual* `docker compose up`) — run `docker compose -f docker-compose.prod.yml down` first if the host actually needs to stay quiet, don't rely on the gate alone. Written, not run, by the AI session per [POLICY.md](../policies/POLICY.md)'s "Deployment and system access" rule — copy/paste these yourself.

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

`app/main.py`'s FastAPI `lifespan` handler calls `ensure_schema()` against the real database automatically on every `auth` container startup (idempotent `CREATE TABLE IF NOT EXISTS`, safe on every restart). Fixed 2026-07-18, see [documentation/bugs/repo/fixed/2026-07-17-postgres-schema-never-initialized-in-production-SOLVED.md](../bugs/repo/fixed/2026-07-17-postgres-schema-never-initialized-in-production-SOLVED.md).

**One-time exception, added 2026-08-12, fixed 2026-08-13** for the `users.username` column ([../plans/deep-singing-firefly.md](../plans/deep-singing-firefly.md) — an opaque per-user storage-path token, [../GLOSSARY.md](../GLOSSARY.md)'s "Opaque token" entry): `ensure_schema()`'s `ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT UNIQUE NOT NULL` only succeeds against zero existing rows — against prod's already-populated `users` table it raises `NotNullViolation` and crash-loops `auth` on every startup attempt. **Do not delete and recreate the accounts to work around this** (tried 2026-08-13, wrong — see [../bugs/claude-bugs/fixed/2026-08-13-recommended-raw-destructive-sql-against-production-instead-of-a-controlled-script.md](../bugs/claude-bugs/fixed/2026-08-13-recommended-raw-destructive-sql-against-production-instead-of-a-controlled-script.md)). Instead, backfill the missing usernames in place, once, before `auth`'s next startup — this runs as a one-off container from the same image, so it works even while `auth` itself is crash-looping:

```
docker compose -f docker-compose.prod.yml run --rm auth python -m scripts.backfill_username
docker compose -f docker-compose.prod.yml up -d
```

No accounts, passwords, or audit history are touched — each row missing a `username` gets one assigned directly (same generation `create_account.py` uses), and `ensure_schema()` becomes a no-op against that column on every startup after.

## 5. Create both accounts

```
CREATE_ACCOUNT_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')"
docker compose -f docker-compose.prod.yml exec -e CREATE_ACCOUNT_PASSWORD="$CREATE_ACCOUNT_PASSWORD" auth python -m scripts.create_account --email joakim.reuterborg@gmail.com --role admin
echo "Password: $CREATE_ACCOUNT_PASSWORD"

CREATE_ACCOUNT_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')"
docker compose -f docker-compose.prod.yml exec -e CREATE_ACCOUNT_PASSWORD="$CREATE_ACCOUNT_PASSWORD" auth python -m scripts.create_account --email elisabeth.reuterborg@gmail.com --role member
echo "Password: $CREATE_ACCOUNT_PASSWORD"
```

Password is read from `CREATE_ACCOUNT_PASSWORD` (generated above so it's not typed into shell history) rather than prompted, since `docker compose exec` isn't a TTY by default here — the final `echo` is the only place it's surfaced, so it can be shared with the account holder immediately and not left sitting in shell history. Fixed 2026-07-18, see [documentation/bugs/repo/fixed/2026-07-17-dockerfile-missing-scripts-directory-SOLVED.md](../bugs/repo/fixed/2026-07-17-dockerfile-missing-scripts-directory-SOLVED.md).

`create_account` also prints a generated `username` (the opaque storage-path token, not typed in — there's no `--username` flag). Once app/'s per-user folder scoping lands (a later increment of the same plan), that value is what each account's `dpfas_media/<username>/` folder will be named — note it down when it prints.

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

## 7. SMTP / invite email delivery (added 2026-08-14)

The `smtp` service (self-hosted, `boky/postfix`, see `docker-compose.prod.yml`) is what `auth` uses to send invite emails (`server/app/mail.py`). It works with zero DNS setup, but mail sent with no DKIM/SPF/DMARC records from a residential IP is very likely to be spam-filtered or rejected outright by Gmail/Outlook — **do this before trusting that an invite email actually arrived, not after**:

1. **Get this server's current public IP** (needed for the SPF record below): `curl -4 ifconfig.me`
2. **Read out the auto-generated DKIM public key** (created on `smtp`'s first startup, persisted in the `smtp_dkim_keys` volume across restarts):
   ```
   docker compose -f docker-compose.prod.yml exec smtp find /etc/opendkim/keys -name '*.txt' -exec cat {} \;
   ```
   This prints a DNS TXT record value (selector `mail` by default) — copy it as-is into the DKIM record below.
3. **Add these DNS records** for `photos.reuterborg.se`, at whatever registrar/DNS host manages it (same place the existing `A` record from the Prerequisites section lives):
   - **SPF** (TXT on `photos.reuterborg.se`): `v=spf1 ip4:<the IP from step 1> ~all`
   - **DKIM** (TXT on `mail._domainkey.photos.reuterborg.se`): the value printed in step 2
   - **DMARC** (TXT on `_dmarc.photos.reuterborg.se`): `v=DMARC1; p=none;` — starts permissive (report-only), tighten to `p=quarantine`/`p=reject` later once delivery is confirmed working, not before
4. **Verify delivery for real** before relying on it: send a test invite to a real Gmail address you control and check whether it lands in the inbox, not spam, and isn't bounced. A tool like [dkimvalidator.com](https://dkimvalidator.com) can confirm DKIM/SPF are actually passing if delivery looks wrong.

If outbound port 25 turns out to be blocked by the ISP (common on residential connections — check this if step 4 fails with a connection-level error, not a spam-folder placement), the whole self-hosted-relay approach needs rethinking; see `documentation/GLOSSARY.md` and this session's design discussion for the alternatives considered and why a third-party email API was ruled out (`POLICY.md`'s closed-by-default rule).

## Stopping / tearing down

```
docker compose -f docker-compose.prod.yml down
```

This does **not** delete the named volumes (`postgres_data`, `analytics_data`, `stories`, `thumbcache`, `caddy_data`, `caddy_config`) — account data, usage analytics, voiceover recordings, and the Let's Encrypt cert all survive a `down` + `up`. Only `docker compose -f docker-compose.prod.yml down -v` would destroy them — never run that without knowing exactly why.

## Test-running the detector service (quality trio + face detection) for real

Added 2026-08-08, alongside `documentation/curation/TODO.md`'s automatic-tagging build plan. The
`detector` service (containerized OpenCV/ONNX models, `documentation/curation/TODO.md` Phase 1-3)
now has a block in `docker-compose.prod.yml`, additive only — it doesn't touch `photo-viewer`'s
existing live `PHOTOS_HOST_PATH`/`momfiles` mount, doesn't need the DB-backed admin photo-source
setting (still unbuilt, see `documentation/plans/tingly-humming-pudding.md`), and doesn't publish a
host port. It takes image bytes over a plain `POST /detect`, so it can be smoke-tested standalone
with one manually-copied photo, entirely independent of the live gallery:

```
cd ~/differentiate-pictures-for-auto-sync
git pull
docker compose -f docker-compose.prod.yml up -d --build detector
docker compose -f docker-compose.prod.yml ps detector

# copy any real JPEG already on the server into the container (or scp one over first)
docker compose -f docker-compose.prod.yml cp /tank/momfiles/<some_real_photo>.jpg detector:/tmp/test.jpg

# real hardware timing, not an estimate
time docker compose -f docker-compose.prod.yml exec detector python -c "
import urllib.request
with open('/tmp/test.jpg', 'rb') as f:
    body = f.read()
boundary = 'X-BOUNDARY'
data = (b'--' + boundary.encode() + b'\r\n'
        b'Content-Disposition: form-data; name=\"file\"; filename=\"test.jpg\"\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + body + b'\r\n--' + boundary.encode() + b'--\r\n')
req = urllib.request.Request('http://localhost:8500/detect', data=data,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
print(urllib.request.urlopen(req).read().decode())
"

# resource use on the real host while it ran (docker stats needs the real container
# name, not the compose service name — Compose v2 prefixes/suffixes it)
docker stats --no-stream $(docker compose -f docker-compose.prod.yml ps -q detector)
```

`docker compose -f docker-compose.prod.yml cp` reads directly off this host's own `/tank` (no need
to route through `photo-viewer`'s mount) — pick any real photo already there, this doesn't write
anything back or modify it. Real per-detector CPU-time breakdown (batches of ~100) and the
admin-configurable source directory (`/tank/dpfas_media`) are now built — see
`documentation/curation/TODO.md`'s "Part A/B" and "Upload into dpfas_media" entries and
`documentation/plans/tingly-humming-pudding.md`. Only the actual `.10` deploy step (`git pull`,
`docker compose -f docker-compose.prod.yml up -d --build`, `mkdir -p /tank/dpfas_media`) is still
outstanding as of 2026-08-08.

**Run for real, 2026-08-08**, against `/tank/momfiles/Florida1/Florida/1/IMGP0128.JPG`: both detector
paths confirmed working on real hardware — quality trio flagged the photo `blurry` (whole-image, no
bbox), face detection (YuNet) found one `Person` with a real bounding box. Round trip was 1.527s, but
that's dominated by `docker exec`/network overhead (client CPU time was ~0.16s), not a clean
per-image inference number — still doesn't answer the real question. `docker stats` after the single
request showed 402MiB / 768MiB (52%) resident — almost certainly the fixed cost of loading OpenCV +
ONNX Runtime + the YuNet model, not a per-image marginal cost, but it means baseline footprint alone
already eats over half the container's memory limit before volume is even a factor. Carry this
forward as a real data point into the resource-benchmarking work below.

## Troubleshooting playbook

Captured 2026-07-17 from the first real P0 deploy, where several of these were worked out live under deadline pressure — reusable steps for "something's broken," roughly in the order that's cheapest-to-check first:

1. **Is this actually a server bug, or a stale browser cache?** Hard refresh (Ctrl+Shift+R) before chasing anything server-side — several "broken" symptoms during the first deploy turned out to be the browser caching failed responses from before auth/schema were fixed.
2. **Did a container restart recently without you asking it to?** `docker compose -f docker-compose.prod.yml ps` — compare "Created" vs "Up" time per service; one showing a much shorter uptime than the others (when you didn't restart it deliberately) means it crashed and `restart: unless-stopped` brought it back. Note: a deliberate `up -d --build` also resets a service's log history (new container instance) - don't mistake that for a crash on its own.
3. **Memory pressure?** `free -h` (host-level) and `docker stats --no-stream` (per-container, against each service's `mem_limit`) - see the `hardware` repo's `server/192.168.1.10/hardware/README.md` for this host's current RAM. Also check `dmesg 2>/dev/null | grep -i "out of memory\|oom-kill"` for a definitive OOM-kill, rather than inferring one from restarts alone.
4. **What does the service's own log say?** Filter out routine noise (uvicorn access logs, and once internet-facing, constant opportunistic bot-scanning 404s for things like `/.env`, `/config.json` - normal, ignore): `docker compose -f docker-compose.prod.yml logs <service> 2>&1
   | grep -iE "error|traceback|exception|killed"`. Grep for the specific
   endpoint/feature too (e.g. `thumb`) - zero matches for an endpoint you know was requested means the request isn't reaching that container at all, which points you at Caddy/routing/the client instead of that service's own code.
5. **Client-side evidence**: browser DevTools Network tab on the actual failing request - exact URL, status code, response body/headers. Cheap and often the fastest way to tell "client never sent it" from "server rejected it" from "server crashed handling it."
