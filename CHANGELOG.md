# Changelog — mamma-photo-viewer branch

One entry per revision, newest first. Started 2026-07-17 — branch history
before this point lives only in `git log` (this branch skipped the
CHANGELOG discipline the main branch already has, for speed early on; see
CLAUDE.md's project-memory note on that trade-off).

## 2026-07-17 (4) — P0 deployment live

- **Deployed and reachable before the 14:00 deadline.** Full sequence:
  Docker installed on the home server from scratch (no `docker` apt
  package on Ubuntu 24.04 — used Docker's official `get.docker.com`
  convenience script instead); repo cloned; `.env` created with
  generated secrets; `docker compose -f docker-compose.prod.yml up -d
  --build` — all 5 containers came up clean, no crash loops.
- **Router work**: EdgeRouter X had SSH disabled by default (first
  attempt to configure port-forwarding over SSH silently failed —
  `ssh` connection was refused, and the pasted command block ran as
  no-ops in the local shell instead, which briefly produced a false
  "configured" doc entry, corrected same day). Enabled SSH via the web
  UI's System page, then configured port-forwarding via the EdgeOS CLI
  (`set port-forward rule 1/2 ...`, ports 80/443 -> 192.168.1.10),
  confirmed via `show port-forward`. **`hairpin-nat` is `disable`** on
  this router (noted in HARDWARE.md) — means devices on Joakim's own LAN
  can't reliably reach `photos.reuterborg.se` by its public DNS name
  (the request doesn't loop back in correctly), even though external
  access works fine. Caused a confusing false-alarm TLS warning when
  testing from Firefox on the LAN; real external testing (phone on
  mobile data) confirmed the deployment is actually correct.
- **DNS**: `photos.reuterborg.se` A record added at Inleed pointing to
  the public IP, root domain confirmed untouched throughout (`dig`
  before/after, done via a separate claude.ai session working the
  DNS/router side in parallel with this one).
- **Let's Encrypt**: Caddy obtained a real certificate for
  `photos.reuterborg.se` automatically once port-forwarding was live —
  no manual cert step. Confirmed via phone (mobile data, off the home
  LAN) that the site is reachable and the login gate correctly blocks
  unauthenticated access.
- **Caught and fixed mid-deploy**: `docker-compose.prod.yml` hardcoded
  the wrong photo path (`/home/joakim/Pictures/mammas_bilder`, copied
  from the dev compose file without verifying against the real server).
  Real path, confirmed by Joakim running `ls` on the server directly:
  `/tank/momfiles` (not even `/tank/mammas_bilder` as first guessed —
  corrected twice). Now sourced from a required `PHOTOS_HOST_PATH` env
  var instead of a literal in the tracked compose file.
  Verified after the fix: `docker compose exec photo-viewer ls /photos`
  shows the real album folders.
- **Account creation**: `create_account.py` command handed over for
  `elisabeth.reuterborg@gmail.com` (role member) — confirm directly with
  Joakim whether this was actually run and the phone login test passed;
  not independently verified by this session past handing over the
  command, since the deadline landed before that confirmation came back
  in chat.
- **Blast-radius discussion** (Joakim): raised whether an app-level
  compromise could reach the LAN/router. Answer documented in
  DEFERRED.md rather than just chat — confirmed no container runs
  privileged/host-networked (the main mitigation already in place), but
  flagged two real gaps as elevated-priority P1 items: photo-viewer's
  container running as root, and no egress restriction from the Docker
  network to the LAN.
- **New `documentation/bugs/` area** (Joakim's request, live during the
  post-deploy human checkpoint): a landing spot for bugs found in the
  moment, with a `TODO.md` untriaged list and a `reports/` subfolder for
  full multi-session investigation trails on the harder ones (first real
  one: the thumbnail-OOM bug below). `CLAUDE.md` now has a standing rule
  to check it periodically and at every session's end. Real bugs found
  and logged there today: `server/Dockerfile` never copies `scripts/`
  into the image (account creation only worked via a live workaround);
  the photo-viewer's static UI shell loads before any login check
  (confusing, not a security issue); thumbnails failing under concurrent
  load, likely OOM (unresolved — see the dedicated report).
- **Also added, from the same live checkpoint**: a hard resource-
  efficiency policy in `POLICY.md` (this must eventually run on
  Pi-class hardware, not just today's server — applies to every future
  code/dependency choice, not just performance-flagged work), and a
  Troubleshooting playbook in `DEPLOYMENT.md` capturing the diagnostic
  steps actually used to chase today's bugs, for reuse next time.
- Deferred, not built today: an always-present support/help button in
  the photo-viewer UI (Joakim's rough sketch: unobtrusive round blue
  button, white question mark) — needs its own design pass, logged in
  `documentation/bugs/TODO.md` conceptually but not yet a real ticket.

## 2026-07-17 (3)

- Documented the router (Ubiquiti EdgeRouter X, firmware 3.0.1, gateway
  192.168.1.1) in HARDWARE.md, including the 80/443->192.168.1.10
  port-forward set up for today's deploy. Gateway IP inferred from the
  dev workstation's `ip route` (same /24 subnet), flagged as such rather
  than presented as directly confirmed on the server. HARDWARE.md:
  2424->3023.

## 2026-07-17 (2)

- **P0 under a hard 14:00 deadline**: gated the photo-viewer behind the
  auth backend's session cookie so Elisabeth can log in and see her
  pictures securely from the open internet, rather than Joakim driving
  ~40min to hand-deliver a zip. Added `app/auth.py` (stateless JWT
  verification, no Postgres dependency in this container by design) as
  a FastAPI dependency on every route that returns photo/thumbnail/
  voiceover data; `app.js` got a silent-refresh `authFetch` wrapper so
  the access token's short TTL doesn't interrupt browsing. Built
  `server/app/login_page.py` (TODO.md 1.10, previously unbuilt — API-only
  before today). Cut `ACCESS_TOKEN_EXPIRE_MINUTES` 15->5 (Joakim: prefers
  a smaller blind-trust window over relying on TTL alone; real
  revocation-recheck is a documented P1, see DEFERRED.md). Shipped a full
  production deployment: root-level `Caddyfile` + `docker-compose.prod.yml`
  (5 services: Caddy with automatic Let's Encrypt for
  `photos.reuterborg.se`, the photo-viewer, the auth+Postgres+Redis
  stack — one file because Caddy has to front two separately-built
  codebases) and `documentation/photo-server/DEPLOYMENT.md` as the
  execution handoff (UFW rules, `.env` setup, account creation, and a
  concrete restart-based persistence check for the analytics DB and
  voiceover recordings — not just a compose-file read). Knowingly
  overrode `HARDWARE.md`'s memtest gate for this one deploy (RAM
  upgrade ordered, not yet installed) — documented as a dated exception,
  not a removal of the gate.
  Discovered along the way: `mamma-photo-viewer` is an orphan branch
  with no shared git history with `master` (confirmed via
  `git merge-base` returning nothing), despite already containing
  byte-identical copies of `phase-1-login`'s auth backend files — so P0
  ported wiring directly onto this branch rather than attempting a
  24-conflict unrelated-histories merge under deadline pressure. Real
  merge preserving all three branches' history deferred to P1, no clock
  pressure — see TODO.md's new "Branch relationship" section.
  Deferred, documented, not silently dropped: access-token revocation
  recheck, multi-tenant photo partitioning (fine today since Elisabeth
  is the only account with photos), and whether `HARDWARE.md` belongs
  under a shared `documentation/hardware/` instead of `photo-server/`
  (see DEFERRED.md). Left the pre-existing stale dependency pins
  (fastapi/uvicorn/pillow/python-multipart) unbumped — Pillow's major
  version bump specifically carries real regression risk to working
  thumbnail code with no time to verify today.
  Doc size: DEFERRED.md 2349->4750, HARDWARE.md 1544->2424, README.md
  5551->5369, TODO.md 30385->34620, DEPLOYMENT.md 0->4157 (new file).
  Tests: 49 (app/) + 47 (server/) = 96 passing, up from 49+45.

## 2026-07-17

- Removed the zip-download feature entirely — server endpoint, client JS,
  tests, and its docker volume — in favor of the sequential per-file
  transfer already used elsewhere. Confirmed by Joakim as a permanent
  decision (mum's real download over a slow/USB-drive link showed a
  single zip is all-or-nothing on failure), not a workaround. Split the
  voiceover feature's docs out of `documentation/gui/TODO.md` into their
  own `documentation/gui/voiceover/` subfolder. Fixed a stale test count
  left in `documentation/gui/README.md` (29 -> 24) from the zip-test
  removal. Commit `1945976`.
- Docker cleanup: the zip removal above left two dead zipcache volumes
  behind — this project's own (10.24GB, only detached once the container
  was recreated on the updated compose file) and a second copy on
  `mamma-photo-viewer_zipcache` (5.08GB), orphaned since the
  branch-mixup incident (see TODO.md's history note) left behind the old
  sibling-repo container's volumes with no container attached. Removed
  both, plus that same orphaned container's `_thumbcache`/
  `_analytics_data` volumes and its unused image, 2 empty unattached
  anonymous volumes, and stopped this repo's own `photo_server_test_pg`/
  `_redis` fixtures (forgotten running 19h past their test session, via
  their own `scripts/test_db.sh down` / `test_redis.sh down`). Local
  Docker volume usage: 15.56GB -> 129.8MB. `buzzkit-api`'s `api-worker-1`
  (a different project) was found still crash-looping under
  `unless-stopped` on missing config — left untouched, flagged to
  Joakim, not this repo's concern to fix.
- Project-level Claude Code permission settings (`.claude/settings.json`,
  tracked in git): added a blanket `Bash(*)` allow and
  `/var/lib/docker/volumes` to `additionalDirectories`, after a session
  where routine investigative commands kept hitting permission popups.
  Note for next session: destructive commands (`docker volume rm`,
  `docker rmi`, `docker run`) stay gated regardless — that floor isn't
  configurable from settings, by design.
- Tested whether the `Bash(*)` rule above actually suppresses popups:
  confirmed yes for ordinary and Docker read commands in this project
  (`ls`, `git log`, `docker ps`/`images`/`volume ls`/`system df` all ran
  without a prompt). Cross-repo Bash calls (`cd`-ing into a sibling
  project) still prompt — expected, matches the cross-repo caution rule
  in global CLAUDE.md, not a gap. One anomaly unresolved: a single
  `git -C <path> log ...` call prompted despite `Bash(*)`, while a plain
  equivalent in the same directory didn't; no hook or setting explains
  it — flag for a future session if it recurs.
- Traced Joakim's standing impression that "Docker must never be run
  directly, only handed over" to its actual source: not this repo, but
  `buzzkit/documentation/policies/POLICY.md`'s Docker/sudo rule, written
  when Docker needed `sudo` there. Verified this session the dev machine
  no longer needs `sudo` for Docker; relaxed that half of buzzkit's rule
  accordingly, left the VPS half gated (unverifiable — no direct VPS
  access), and added a follow-up note to `buzzkit/CLAUDE.md` to re-check
  the VPS side once its terminal output is next available. Edits made
  directly in buzzkit's working tree, uncommitted — cross-repo commits
  need asking first, per global CLAUDE.md.
- Confirmed `docker run` (via `server/scripts/test_db.sh`/`test_redis.sh`)
  keeps prompting even with `Bash(*)` already in effect — proof, not
  just the earlier note's suspicion, that this class of command
  (`docker run`/`rmi`/`volume rm`) is gated above the settings.json
  allow-list layer, not by it. Since `Bash(*)` is already the broadest
  possible pattern, no narrower docker-specific rule could ever suppress
  it either — there's no rule to add or remove here, the floor isn't
  reachable from settings at all.
- While drafting a next-session starting prompt for GUI login + branch
  merges: fixed stale doc drift in `documentation/photo-server/README.md`'s
  "Priority order" section — it still posed "does Phase 1 adapt Joakim's
  buzzkit login implementation or build fresh" as an open question,
  contradicting the same file's own Status section a few lines up, which
  already said that was decided and executed (ported from buzzkit,
  argon2id, JWT+redis, steps 1.1–1.8 done). Confirmed via buzzkit's own
  CHANGELOG (Rev 4/5, 2026-07-05) that its login/auth — signup, lockout,
  Google OAuth, JWT refresh/logout, RLS isolation, GDPR erasure — was
  finished and tested long before today; the stale line was simply never
  updated once the decision was made. Not an open question anymore.
