# Changelog

One entry per revision, newest first. This file merges two changelog histories that grew independently after `mamma-photo-viewer` forked as an orphan branch (2026-07-16, no shared git history with `master`) — folded back into one surviving `master` on 2026-07-21 (see [photo-server/TODO.md](documentation/photo-server/TODO.md)'s "Branch relationship" note). Entries from 2026-07-17 through the merge are `mamma-photo-viewer`'s own changelog, newest first; entries from 2026-07-16 backward are this repo's original mainline history, continuing unbroken from 2026-07-15. Never rewrite or reorder past entries in either half. Entries from 2026-07-19T03:42:35+00:00 onward head same-day entries with a UTC ISO 8601 timestamp instead of a `(N)` counter (see CLAUDE.md's changelog rule); earlier `(N)`-numbered headings, including the 07-19 duplicate `(3)`, are left exactly as originally written.

## 2026-07-23T13:46:53+00:00 — claude-bugs report: real account password passed via scripted CLI flag, repeated in chat

Joakim flagged, correctly, that creating the local dev environment's two real accounts via `docker compose exec -e CREATE_ACCOUNT_PASSWORD=... auth python -m scripts.create_account` passed the real chosen password as a scripted CLI-visible env var instead of using the script's own interactive prompt — exactly what its docstring warns against (shell-history/process-listing exposure) — and that the password then got repeated in the chat transcript across two turns. Filed as `documentation/bugs/claude-bugs/under_process/2026-07-23-real-account-password-passed-via-scripted-cli-flag-and-repeated-in-chat.md`.

Investigated before writing the report, per CLAUDE.md's "ask or search, never guess" rule, since Joakim's framing ("given the whole internet... access to the web admin... writing it in the repo") didn't match what was checkable: `git grep` across every commit in the repo's history found the password in no tracked file, ever, and the local stack's only host-published port (Caddy) is bound to `127.0.0.1:8420` specifically — not the LAN, not the internet; postgres/redis/auth publish no host ports at all. The bug file records the corrected scope (CLI/shell-history and chat-transcript exposure, not a repo commit or internet-facing one) alongside the real lapse, so a later reader gets the accurate version, not the original alarming one.

- **Doc size**: `documentation/bugs/claude-bugs/under_process/2026-07-23-real-account-password-passed-via-scripted-cli-flag-and-repeated-in-chat.md` 0 → 4,168 (new; caught and redacted one further near-miss while drafting it — the reproduction snippet originally quoted the literal password, which would have committed it to the repo for the first time. Replaced with `<redacted>` before staging).

## 2026-07-23T13:17:23+00:00 — session wrap-up: checks re-verified, one forward-effectiveness note

Ran the session wrap-up checklist (`documentation/tooling/README.md`): `commit_cost/check_coverage.sh`'s one "missing" hit was this session's own last logging commit — the documented, expected one-commit lag, not a real gap. No dangling Docker images, no running containers left (`docker compose down` was run after verification). Dead-link sweep clean. No loose ends in the chat — the OAuth question, the photo-source question, and the multi-user-features sequencing question were all resolved via explicit choices, not left open. No stale TODOs found beyond what the two entries above already closed out.

**Forward-effectiveness note**: this session spent real effort re-deriving that `gui/TODO.md`'s login section was stale (cross-checking `git log`, `CHANGELOG.md`, and the actual code in `app/main.py`/`app/auth.py` to confirm login had actually shipped under P0 deadline pressure without a doc update alongside it). When a deadline-driven change ships without time to update every affected doc, leaving one explicit `**doc update deferred**` marker at the change's own CHANGELOG entry (pointing at exactly which doc/section is now stale) would let a later drift-fix jump straight there instead of rediscovering the gap by diffing prose against code from scratch.

## 2026-07-23T13:10:14+00:00 — logged three multi-user feature gaps to DEFERRED.md (upload, shared media root, rename+original-name audit log)

Joakim flagged three prerequisites for the coming multi-user work while the auth-policy consolidation above was in progress: an upload function, a shared media folder that disregards file ownership at the storage layer (view authorization only, app-side), and the ability to rename a file with the original name/folder logged in the database for a future native per-device sync app to reconcile against. Asked to just log these for now, not design or build them yet. Added as new `DEFERRED.md` entries; the shared-folder one turned out to already be exactly the "Single consolidated media root for P1+" item logged 2026-07-17, so reconfirmed/cross-referenced that one rather than duplicating it — upload and the rename-audit-log are genuinely new entries.

- **Doc size**: `documentation/photo-server/DEFERRED.md` 10,629 → 11,541 (+912).

## 2026-07-23T13:04:37+00:00 — working local full-stack dev environment, and a new project-wide AUTHENTICATION.md

Joakim wants to develop locally going forward. The root `docker-compose.yml` was stale (flagged 2026-07-19, never fixed) — it predates `app/auth.py`'s login requirement and would crash at startup. Rebuilt it into a real local mirror of `docker-compose.prod.yml`: caddy + photo-viewer + `server/`'s auth backend + postgres + redis, five services, all working end-to-end. Two deliberate local-only divergences from prod, both scoped to "never leaves this machine": every credential is a fixed, checked-in, obviously-fake value ("local-dev-only...") instead of a `.env` (nothing there is worth protecting — no host port published except via Caddy on `127.0.0.1`), and Caddy serves plain `http://localhost` instead of a self-signed cert (Chromium treats `http://localhost` as a secure context, so the `Secure`-flagged session cookie and the File System Access folder-picker both still work). New `Caddyfile.local` routes `/login`/`/whoami`/`/refresh`/`/logout` to `auth`, everything else to `photo-viewer`, same split as production's `Caddyfile`. Photos mount read-only from the real `/home/joakim/Pictures/mammas_bilder` (confirmed with Joakim, not the real library by default per CLAUDE.md's high-blast-radius rule — but this app is read-only against `/photos` in every deployment, downloads only copy out) rather than a synthetic fixture. Verified live: built both images, brought up all five containers clean, created the project's two real accounts (`joakim.reuterborg@gmail.com` admin, `elisabeth.reuterborg@gmail.com` member) via `server/scripts/create_account.py`, logged in through Caddy, and confirmed `/api/tree` returns the real album tree using the session cookie — full login-to-gallery flow working locally for the first time. Accounts persist in the `postgres_data` named volume across `down`/`up`.

Found and fixed real doc drift while in this area: `gui/TODO.md`'s login section still called the backend login architecture "genuinely open" and login itself "not started," both stale since the 2026-07-17 P0 deploy (`9c090b0`) actually shipped and gated every API route behind it; the "branch state" note describing an unresolved `phase-1-login`/`master`/`mamma-photo-viewer` merge was stale since that merge completed 2026-07-21; the "Real TLS" requirement was stale since production has run behind a real Let's Encrypt cert since 2026-07-17.

Joakim then asked about OAuth for the coming multi-user work and whether local dev would need to be secure for it — surfaced that this was already answered 2026-07-16 (`photo-server/TODO.md`'s Phase 1 note): third-party/social OAuth conflicts with `POLICY.md`'s closed-by-default/no-cloud-APIs rule, so it's excluded, not just deferred; passkeys/WebAuthn (a W3C standard, no third-party relying party) stay compatible and remain a real priority item. Consolidated this and the rest of the auth requirement list — previously scattered across `gui/TODO.md` and `photo-server/TODO.md` — into one new project-wide file, **`documentation/policies/AUTHENTICATION.md`**, grounded in fresh research (logged per `~/.claude/CLAUDE.md`'s research-log rule): current authority is NIST SP 800-63-4 (Rev 4, effective 2025-08-01) for password length/composition, OWASP's Authentication Cheat Sheet for passkeys-as-current-direction, and Troy Hunt's k-anonymity writeup plus a self-hosted option (IncogniPwn) for the breach-password check so it can stay inside closed-by-default rather than calling the live `haveibeenpwned.com` API. Per Joakim's explicit instruction, every other doc that used to carry this detail now only points at `AUTHENTICATION.md` — `gui/TODO.md`'s login section, `gui/README.md`'s known-limitations bullet, and `photo-server/TODO.md`'s OAuth-exclusion clause were all trimmed to references, not left duplicated. Added `documentation/policies/README.md` (didn't exist before — `policies/` only ever held the single `POLICY.md`) to index both files now that there are two. `tools/documentation_checks/run.py` clean (no dead links) after.

- **Doc size**: `documentation/gui/README.md` 8,157 → 9,348 (+1,191). `documentation/gui/TODO.md` 17,917 → 14,856 (-3,061, net of removing now-duplicated auth detail). `documentation/policies/AUTHENTICATION.md` 0 → 6,565 (new). `documentation/policies/README.md` 0 → 721 (new). `documentation/photo-server/TODO.md` 38,674 → 38,935 (+261). `documentation/README.md` 1,032 → 1,078 (+46).

## 2026-07-21T02:53:54+00:00 — wrap-up for the bugs/ restructure: coverage/hygiene checks, one forward-effectiveness note

Ran the session wrap-up checklist (`documentation/tooling/README.md`): `commit_cost/check_coverage.sh`'s one "missing" hit was the logging commit itself — the documented, expected one-commit lag, not a real gap. Disposable `test_db.sh`/`test_redis.sh` containers and volumes confirmed fully torn down (only the two now-cached base images remain, already flagged to Joakim as reusable, not abandoned). Dead-link sweep re-run clean. No loose ends in the chat, no stale TODOs resolved-but-still-open.

**Forward-effectiveness note**: splitting `claude/` into `fixed/`/`under_process/` required reading every file's tail in full to judge resolved-vs-open, since claude-bugs entries have no `Status:` line the way `repo/` entries already do. Logged as a candidate in [claude-bugs/TODO.md](documentation/bugs/claude-bugs/TODO.md) — adopting the same convention would turn that judgment call into a grep.

- **Doc size**: `documentation/bugs/claude-bugs/TODO.md` 270 → 697 (+427).

## 2026-07-21T02:46:50+00:00 — bugs/ tracker restructured to match global CLAUDE.md's prescribed layout

Joakim pointed out `documentation/bugs/` (`claude/`, `reports/`, `solved/`) didn't actually match the per-project bug-tracker layout `~/.claude/CLAUDE.md` describes (`claude-bugs/{fixed,under_process}/`, `repo/{fixed,under_process}/`). Restructured to match: `claude/` split into `claude-bugs/fixed/` (11 already-resolved lapses) and `claude-bugs/under_process/` (2 still open — the bug-tracking token-cost question and the wrap-up-length question, both explicitly deferred pending Joakim's input); `reports/` renamed to `repo/under_process/`; `solved/` renamed to `repo/fixed/` (kept the existing `-SOLVED` filename suffix there — new-status-via-folder-alone is the convention going forward, but renaming 6 already-solved files too would have broken every existing link to them for no benefit). All moves used `git mv` to preserve file history.

`tools/create_bug_report/create_bug_report.sh` and `mark_solved.sh` updated for the new paths; `mark_solved.sh` now takes an optional `--claude` flag (mirroring `create_bug_report.sh`) and moves `under_process/` → `fixed/` within whichever category, without imposing a `-SOLVED` suffix on claude-bugs (that folder never had one). Both smoke-tested end to end (create → mark solved, one throwaway file per category, cleaned up after). `tools/documentation_checks/run.py`'s `EXEMPT_FROM_TODO` list dropped `bugs/solved`/`bugs/claude` (gone) — `claude-bugs/` and `repo/` now each get a real `TODO.md` since both hold genuine open work in `under_process/`, unlike before.

Every cross-reference to the old paths updated across the repo (`CLAUDE.md`, `documentation/tooling/*`, `documentation/gui/TODO.md`, `documentation/photo-server/*`, `app/main.py`, `docker-compose.prod.yml`, `server/tests/test_dockerfile_build.py`) plus a few relative-link depth fixes inside the moved bug files themselves (they now sit one level deeper). Also fixed 5 markdown links in this file's own past entries that pointed at the old paths — link-target-only, no prose rewritten, since a "see X" link has to actually resolve (CLAUDE.md's cross-reference rule) even when the entry describing it is otherwise frozen. `tools/documentation_checks/run.py` clean (zero broken links) after. `app/tests` (53) and `server/tests` (49, 1 docker-marked deselected, run against disposable `test_db.sh`/`test_redis.sh` fixtures, torn down after) both green — no app/server logic touched, only doc/comment paths and the two bug-report scripts.

- **Doc size**: `documentation/bugs/` 82,463 → 82,112 (-351, net of the fixed/under_process split plus reworded READMEs/TODOs). `CLAUDE.md` 15,940 → 15,994 (+54). `documentation/tooling/README.md` 4,501 → 4,539 (+38). `documentation/tooling/DOCUMENTATION_CHECKS.md` 2,590 → 2,535 (-55). `documentation/gui/TODO.md` 17,863 → 17,917 (+54). `documentation/photo-server/README.md` 6,169 → 6,211 (+42). `documentation/photo-server/TODO.md` 38,651 → 38,674 (+23). Smaller (≤16 char) fixes in `documentation/tooling/{REDUNDANCY_SCAN,TODO,CLEANING}.md`, `documentation/photo-server/{TOOLCHAIN,DEPLOYMENT,HARDWARE}.md` not itemized individually.

## 2026-07-21T02:02:31+00:00 — merge master, phase-1-login, and mamma-photo-viewer into one surviving master

Joakim asked to merge this repo into `master`. Per the P1 plan already on file (photo-server/TODO.md's "Branch relationship" note, 2026-07-17): folded `phase-1-login` into `master` first (clean fast-forward, zero conflicts, as expected — `master` was a real ancestor), pushed; then merged `master` into `mamma-photo-viewer` via `git merge --allow-unrelated-histories` (the two share no git history at all — `mamma-photo-viewer` is an orphan branch, root commit "Initial empty commit"), resolving 33 real file conflicts (more than the 24 found 2026-07-17, since both branches kept moving) — history preserved throughout, nothing squashed or cherry-picked. Ran `master` into the feature branch first rather than the reverse, per CLAUDE.md's merge-mechanics rule, so `master` stayed untouched until a single, guaranteed-clean fast-forward at the very end.

Real architectural collision found and resolved, not just textual conflicts: both branches' `app/` directories were live, unrelated products at the same path — `master`'s original file-differentiation tool (opencv/numpy/mysql-based dedup+sort, this repo's namesake purpose) versus `mamma-photo-viewer`'s actively-deployed FastAPI GUI photo-viewer. Joakim's call: the live product keeps `app/`; the original tool moved to `prototypes/differentiate_pictures/` (not deleted — it's prototype/reference material for this folder's own planned server-side analysis backend, "next step" after photo-viewer fixes, not obsolete). `documentation/picture-handling/README.md`/`TODO.md` updated to point at the new path. Root `requirements.txt` split the same way (photo-viewer deps stay at root; the old tool's deps moved with it).

For every other conflicted file (config, docs, the two append-only `tools/*/*.jsonl` logs), `mamma-photo-viewer`'s side was consistently the later, more-evolved superset — verified per file via whitespace-normalized diff before taking it wholesale, not assumed. `CHANGELOG.md` (this file) is the one genuine synthesis: both branches' independent changelog histories are concatenated, `mamma-photo-viewer`'s entries (2026-07-17 onward) on top, master's original history (through 2026-07-15) below a seam marker — neither history rewritten. `documentation/photo-server/TODO.md`'s "Branch relationship" section rewritten to record the merge as done rather than pending.

Verified clean: 53 `app/tests` + 49 `server/tests` (1 docker-marked test correctly deselected) all pass post-merge; no leftover conflict markers anywhere in the tree (`git grep`); `git fsck --full` clean (a mid-session full-computer hang left no repo damage — checked before resuming, only harmless dangling objects, no lock files, no truncated writes).

- **Doc size**: `CHANGELOG.md` 127,825 → 130,962 (+3,137, this entry). `documentation/photo-server/TODO.md`, `documentation/picture-handling/README.md`/`TODO.md` also edited this session — see `tools/doc_metrics/metrics.jsonl` for exact per-file deltas once logged.

## 2026-07-20T22:17:23+00:00 — move the security-analysis rule's mechanics out of global CLAUDE.md, into bugs/solved/README.md

Joakim caught that the just-added global rule belonged in this repo's own bug-tracker docs, not restated in `~/.claude/CLAUDE.md` — matching this project's existing pattern (project CLAUDE.md already points bug-tracking mechanics at `documentation/bugs/README.md`/`claude/README.md` rather than repeating them). Trimmed the global bullet down to the principle + a pointer; moved the concrete "append a Security analysis section on move, raise real risks directly" instruction into [bugs/solved/README.md](documentation/bugs/repo/README.md), next to its existing "On move: rename the file..." bullet.

- **Doc size**: `documentation/bugs/solved/README.md` 666 → 1492 (+826).

## 2026-07-20T22:14:33+00:00 — new global rule: security analysis in the bug file, not just chat

Joakim asked "is your fix safe?" after the Redis-persistence fix and only got the analysis because he asked — it existed in chat, not in the bug's own record. He made it a standing global CLAUDE.md rule: every bug fix/feature gets a security-analysis addendum written into its own durable file, and any real (non-theoretical) risk found gets raised to him directly. Applied it retroactively here: added a "Security analysis" section to [the Redis bug's solved file](documentation/bugs/repo/fixed/2026-07-18-redis-has-no-persistent-volume-every-restart-wipes-active-sessions-SOLVED.md) (no new attack surface, lower-sensitivity data than what's already in the same trust boundary, one real-but-bounded residual risk: an unclean shutdown could in principle corrupt Redis's AOF and block startup until repaired, mitigated by Redis 8's multi-part AOF auto-truncation) and logged the un-mitigated follow-up (a health check that alerts instead of silently crash-looping) in [photo-server/TODO.md](documentation/photo-server/TODO.md)'s security checklist.

- **Doc size**: `2026-07-18-redis-...-SOLVED.md` 4721 → 6660 (+1939); `photo-server/TODO.md` 38173 → 38948 (+775).

## 2026-07-20T22:06:47+00:00 — session wrap-up: full checklist, no drift found

Session-close sweep per [tooling/README.md](documentation/tooling/README.md)'s checklist: `app/tests` already green from earlier this session (no `app`/`server` code touched since — only `docker-compose.prod.yml` and docs, so not re-run); secrets-in-diff scan clean on every commit; `doc_metrics`/`commit_cost` logged after each commit (steady-state one-commit lag on the last logging commit itself, expected per COMMIT_COST.md); `tools/documentation_checks/run.py` clean (dead links, topic `TODO.md`s, stub sizes); the doc-path comment added to `docker-compose.prod.yml` resolves to the real moved file; no dangling Docker images and no leftover containers/volumes from this session's throwaway redis-persistence test; no manifest/lockfile changed; skimmed `documentation/bugs/reports/` — the 12 other open bugs are all unrelated to this session's redis fix, none stale. No unanswered questions or dropped "I'll get back to you" threads in this session's chat.

**Forward-effectiveness note**: handing over a copyable command that runs `docker compose up -d <service>` immediately followed by an `exec ... redis-cli ping` in the same block cost one avoidable back-and-forth this session — Compose reports a container "Started" before the process inside has actually finished booting (here: before `redis-server` had loaded/created its AOF files), so the immediate `exec` raced it and returned a scary-looking "Connection refused" that turned out to be nothing. Next time: split `up -d` and the first `exec`/`ping` into separate steps in the handoff, or note explicitly that a "Connection refused" right after `up -d` may just be this race, so it doesn't read as a real failure needing diagnosis.

- **Doc size**: `CHANGELOG.md` 78648 → 80505 (+1857).

## 2026-07-20T22:02:01+00:00 — verify the Redis persistence fix against production

Joakim redeployed the fix below on the real server and ran the actual restart test: logged in, opened an album, restarted the `redis` container, then loaded a photo and a different album from the same still-open tab with no reload or re-login - both loaded normally, confirming the session survived. Updated [the bug report](documentation/bugs/repo/fixed/2026-07-18-redis-has-no-persistent-volume-every-restart-wipes-active-sessions-SOLVED.md) with the production verification.
- **Doc size**: `2026-07-18-redis-...md` 3985 → 4721 (+736).

## 2026-07-20T21:53:30+00:00 — give Redis a persistent volume so container restarts stop wiping every login session

Fixed the confirmed-root-cause bug from 2026-07-18: `docker-compose.prod.yml`'s `redis` service had no `volumes:` entry at all, so any restart (crash, reboot, `docker compose down`/`up`) silently deleted every issued refresh token, logging everyone out with no visible error until their 5-minute access token happened to expire. Added a named `redis_data` volume mounted at `/data` (same pattern as `postgres_data`) and `--appendonly yes` to the redis command so writes are actually fsynced to it. Verified locally with a disposable, same-image/same-flags throwaway container: set a key with a TTL, restarted the container, confirmed the key and its remaining TTL both survived. Not yet verified against the real production stack — restarting prod redis is a live action, handed to Joakim to run and confirm a real session survives it before fully trusting this end-to-end. Moved [the bug report](documentation/bugs/repo/fixed/2026-07-18-redis-has-no-persistent-volume-every-restart-wipes-active-sessions-SOLVED.md) to `solved/`.
- **Doc size**: `2026-07-18-redis-...md` 3031 → 3985 (+954, moved reports/ → solved/).

## 2026-07-20T21:27:17+00:00 — session wrap-up: cross-reference the new bug, forward-effectiveness note

Session-close sweep: `tools/documentation_checks/run.py` clean (dead links, topic `TODO.md`s, stub sizes), no dangling Docker images/containers, `python -m unittest` (29 tests across `redundancy_scan`/`documentation_checks`/`doc_metrics`) green - `app/`/`server/` untouched since the last full test run this session, so not re-run. Added the still-missing cross-reference from `documentation/gui/TODO.md` to today's new Ishotellet bug report, matching the existing pattern for other open bugs in that file (e.g. the lightbox bug).

**Forward-effectiveness note**: the stale hard-wrap found in `create_bug_report.sh` (fixed earlier this session) is a specific instance of a general gap - the 2026-07-16/19 repo-wide convention drop only touched *existing* files, never checked code that *generates* docs (shell-script templates, `cat <<EOF` blocks). A future repo-wide convention change should explicitly grep `tools/*/`'s heredocs/templates too, not just `*.md` files, or the old convention keeps quietly reproducing itself in every new file the tool creates.

- **Doc size**: `documentation/gui/TODO.md` 17486 → 17863 (+377).

## 2026-07-20T21:24:04+00:00 — record Ishotellet's real file count/size in the bug report

Joakim ran `find Ishotellet -type f | wc -l` / `du -sh Ishotellet` directly on the server from `/tank/momfiles`: 354 files, 718M. Logged into the investigation log as the size data point the report's "next session" note was waiting on. Also fixed a leftover hard-wrapped Status line in that same file (created just before the template fix in the previous entry, so it still carried the old wrapping).
- **Doc size**: `2026-07-20-ishotellet-...md` 2204 → 2570 (+366).

## 2026-07-20T21:14:43+00:00 — file the Ishotellet bottom-first thumbnail-load bug; fix a stale hard-wrap in the bug-report template

Joakim flagged, in passing, that the "Ishotellet" album's thumbnails visibly loaded bottom-of-page first during the thumbnail-OOM re-test above — confirmed via a clarifying question this means render order, not page auto-scroll. Filed as its own investigation-open file per CLAUDE.md's bug-report rule, not left as a chat aside: [2026-07-20-ishotellet-album-thumbnails-load-bottom-first-instead-of-top-first.md](documentation/bugs/repo/under_process/2026-07-20-ishotellet-album-thumbnails-load-bottom-first-instead-of-top-first.md). Leading theory (unconfirmed): native `loading="lazy"` on grid thumbnails interacting unexpectedly with a large album's layout - needs a live DevTools repro, not chased down yet.

Also fixed, found while filling in the report: `tools/create_bug_report/create_bug_report.sh`'s two templates still hard-wrapped their placeholder prose to a fixed column, a leftover from before the repo-wide "one paragraph per line" convention was dropped (2026-07-16/19) - every bug report generated since then inherited that stale wrapping in its placeholder text. Joined the wrapped lines; existing `test_create_bug_report.sh` still passes (doesn't assert on wrapping).

- **Doc size**: new bug report file, 2204 chars. `create_bug_report.sh` unchanged in size (2089 → 2089, pure rewrapping).

## 2026-07-20T21:07:59+00:00 — re-confirm thumbnail-OOM mitigation live; shelve the pre-compile-thumbnails build

Resumed the paused live-GUI bug-test cycle. Joakim re-tested thumbnail loading on `photos.reuterborg.se` against an uncached album — no broken images, no unresponsiveness, just consistent per-thumbnail latency: matches the existing "mitigated, not fully fixed" status exactly, logged in the thumbnail-OOM report's investigation log.

He then asked to build the already-designed pre-compile-thumbnails fix, with three added requirements (cache alongside the photo files instead of its own volume, cleanup on a delete-flag, multi-user readiness). Investigated before building (no code written) and found real forks in all three: the photos mount is read-only in both compose files, no delete-flag feature exists anywhere in the running service to hook into, and no per-user ownership model exists yet either. Computed real disk-size numbers along the way: current 340×340/quality-82 thumbnails run ~15-30KB each, so even 20,000 of them (~400MB) is under 0.02% of the server's 2.7TB free ZFS space — disk size was not actually a blocking constraint by the numbers. Joakim opted to shelve the build anyway and wait for the incoming RAM upgrade to see if it addresses the latency differently, rather than take on the added scope now.

- **Doc size**: `2026-07-17-thumbnail-oom-under-load.md` 5718 → 6242 (+524), `2026-07-17-pre-compile-thumbnails-ahead-of-time.md` 3315 → 5486 (+2171), `documentation/gui/TODO.md` 17507 → 17486 (-21).

## 2026-07-20T20:48:10+00:00 — formalize the documentation cleaning protocol: ordering, a new script, referenced from CLAUDE.md

Joakim asked for an explicit cleanup protocol (with scripts, not just prose) covering three specific rules: prefer a cross-reference over duplicated content, actively compact/merge prose rather than only deleting exact duplicates, and keep `CLAUDE.md` itself shrinking over time. `CLEANING.md` already existed (built 2026-07-19) but had never been referenced from `CLAUDE.md` itself, and the redundant-phrase scan used in yesterday's cleaning pass (2026-07-20T19:43:47+00:00 entry) was done ad hoc, not as a real tool.

- **New**: `tools/redundancy_scan/` — surfaces markdown phrases repeated verbatim across 2+ files via `difflib.SequenceMatcher` (maximal matching runs, not fixed n-gram windows, so a long repeated block is one match, not a dozen overlapping ones). TDD'd (7 tests, `test_scan.py`), always exits 0 (a match is a candidate for review, never an automatic fix — matches CLEANING.md's existing "fix vs. flag" principle). See `documentation/tooling/REDUNDANCY_SCAN.md`.
- **`CLEANING.md` rewritten** with an explicit ordered protocol instead of an unordered checklist: run scripted checks first (dead-link sweep + the new redundancy scan), then check whether a duplicate should become a cross-reference *before* independently compacting either copy, then compact whatever must stay in place, then a new step 6 - `CLAUDE.md` specifically should shrink or hold, not grow, verified via a one-line `doc_metrics` jsonl grep rather than impression.
- **`CLAUDE.md` now references `CLEANING.md`** (it didn't before) from its existing "Lean, exact, and compact" rule, one sentence, matching that rule's own no-restating principle rather than duplicating CLEANING.md's content inline.
- Registered the new stub `tools/redundancy_scan/README.md` with `documentation_checks`' own stub-size check; `documentation/tooling/README.md`'s index updated.
- **`CLAUDE.md` grew this pass (+488 chars)**, which its own new step 6 flags as needing an explicit reason rather than silent creep: this is that reason — a genuinely new pointer to protocol/scripts that had nowhere else to live yet, not accumulated detail. Future *cleaning* passes (as opposed to this kind of new-infrastructure pass) are still expected to shrink or hold it.
- Verified: `tools/documentation_checks/run.py` clean, `python -m unittest` (29 tests across `redundancy_scan`/`documentation_checks`/`doc_metrics`) and `app/tests` (53) all green.
- **Doc size**: `CLAUDE.md` 15452 → 15940 (+488), `documentation/tooling/CLEANING.md` 3666 → 7162 (+3496), `documentation/tooling/README.md` 4301 → 4501 (+200), `documentation/tooling/REDUNDANCY_SCAN.md` new at 3150.

## 2026-07-20T20:36:39+00:00 — document the production server's SSH user

Joakim asked me to remember the server's SSH user (`joakim`) for future pull/restart commands — recorded in `HARDWARE.md`'s hardware table (the existing "how to reach 192.168.1.10" home) instead of private AI memory, per this repo's self-sufficiency rule: a fresh session or a human dev needs this fact too, not just this conversation. `DEPLOYMENT.md` now opens with the explicit `ssh joakim@192.168.1.10` step, pointing at HARDWARE.md's table rather than repeating the user inline a second place.
- **Doc size**: `HARDWARE.md` 5013 → 5037 (+24), `DEPLOYMENT.md` 7560 → 7649 (+89).

## 2026-07-20T20:18:54+00:00 — remove the upfront folder-choice screen, offer it lazily instead

Built the download-folder UX rework flagged as designed-but-not-built in `documentation/gui/TODO.md`'s "Open from the 2026-07-18 session" — Joakim asked to implement it after finding the note. On a new branch `mamma-photo-viewer-folder-ux` (off `mamma-photo-viewer`), per CLAUDE.md's ask-before-new-branch rule.

- **Removed**: the `#setup` screen (`<h1>Mammas bilder</h1>` + "choose folder"/"skip" buttons) that used to block the gallery on every load without a restorable folder handle. The gallery now shows immediately.
- **Added**: `maybeOfferFolderPicker()` in `app.js` offers the native folder picker lazily, the first time any save action happens (single lightbox download or bulk) — not upfront. A decline, cancel, or unsupported browser is remembered forever (`localStorage`'s `mpv_folder_prompt_done`), so it never asks again; re-picking afterward happens only via clicking the toolbar's folder-status label, now a real `<button>` (`#downloadFolderLabel`).
- **Deviation from the original TODO note, confirmed via a web search before implementing** (logged in `~/.claude/research_log.jsonl`, MDN/Chrome docs): "hoverable to show the full path" isn't achievable — `FileSystemDirectoryHandle` only ever exposes the picked folder's own `.name`, never a full OS path, by deliberate browser privacy design. The hover title shows the folder name instead; flagged to Joakim and confirmed before building rather than silently dropped or guessed around.
- TDD: 5 new Selenium tests (`app/tests_selenium/test_folder_prompt.py`) written and confirmed failing for the right reason before implementation; `conftest.py` and 3 existing Selenium tests that clicked the now-removed `skipFolderBtn` updated to match. `app/tests` (53) and `app/tests_selenium` (13) both green.
- **Doc size**: `documentation/gui/README.md` 7810 → 8157 (+347), `documentation/gui/TODO.md` 16741 → 17507 (+766).

## 2026-07-20T19:43:47+00:00 — trim genuine cross-file redundancy, found by scanning for repeated phrases

Joakim asked for a pass reading every doc for redundancy and cutting characters "by making the text more reliable" — with an explicit flag on my part first that this project's own CLEANING.md warns against optimizing for char count over correctness, and CLAUDE.md requires `Why:` reasoning to stay attached to rules, not get stripped for size. Used an objective signal instead of subjective judgment calls: scanned every file (except the append-only CHANGELOG.md) for word-sequences repeated verbatim across 2+ files, at both a 12-word and 10-word window, then manually reviewed every group found rather than cutting on the signal alone.

- **Fixed — genuinely stale duplication**: 5 files under `bugs/claude/` (`2026-07-18-claimed-a-doc-edit-...`, `2026-07-18-promised-a-follow-up-...`, `2026-07-19-asked-inline-...`, `2026-07-19-didn-t-create-bug-report-...`, `2026-07-19-used-unexplained-ad-hoc-labels-...`) each opened with a full sentence restating `bugs/claude/README.md`'s own definition of what belongs in that folder — the exact sentence `tools/create_bug_report/create_bug_report.sh`'s `--claude` template used to generate, before an earlier same-day pass (see the `(6)` entry below) trimmed the *template* to just a pointer. These 5 files predated that fix and never got the same trim. Now match the current template's output: a bare `See [README.md](README.md) for what belongs here.` pointer, nothing restated.
- **Fixed — restated a project-wide rule instead of pointing at it**: `COMMIT_COST.md`/`DOC_METRICS.md` both opened with an identical clause explaining CLAUDE.md's documentation-layout rule in full (`— all documentation lives under `documentation/`, including tooling notes`) instead of just citing it — exactly the pattern CLAUDE.md's own "nothing project-wide duplicated outside POLICY.md" line warns against. Trimmed both to point at the rule, not restate it.
- **Reviewed and left alone, with reasoning**: 9 more repeated-phrase groups the scan surfaced — table-header markdown syntax (not content); `bugs/README.md`/`bugs/claude/README.md` both stating the one-file-per-lapse naming rule (each needs to stand alone per this repo's self-sufficiency principle, so a reader landing on either file directly still gets the rule); the still-current `create_bug_report.sh` report template's own boilerplate (`Status: **investigating, not fixed**...`) appearing in every open bug report, because it's the *current*, intentional template output, not stale; `gui/README.md`'s one-line feature summary echoing `voiceover/README.md`'s fuller description (a summary is supposed to echo the thing it summarizes); CLAUDE.md's own rule text quoted inside the two `bugs/claude/` reports that document a violation of that exact rule (citing the rule you broke is the point of an incident report, not duplication to cut).
- Re-verified: `tools/documentation_checks/run.py` clean, `app/tests` 53 passed. `server/tests` not re-run — doc-only.
- **Doc size**: 69 tracked `.md` files, 314,013 → 313,253 characters (**-760**).

## 2026-07-19T04:39:12+00:00 — drop the hard-wrap convention repo-wide: one paragraph/item per line

Joakim pushed back on an earlier claim in this same session (that keeping hard-wrap protected `git diff`/`git blame` granularity) after I tested it with a same-length word swap rather than a realistic edit. Re-tested with a realistic edit (inserting a clause, then re-wrapping, which is what actually happens): hard-wrap reflows every line after the insertion point too, so it does **not** preserve isolated single-line diffs for normal edits — that argument didn't hold up. Measured the actual character cost instead: hard-wrapping adds a newline+indent at every wrap point that an unwrapped line doesn't pay, confirmed at 1.4–1.45% of total doc size across the real corpus.

- **Wrote and TDD-verified a one-time de-wrap script** (scratchpad, not checked in — this is a single mechanical reformat, not a recurring tool, unlike `documentation_checks/`). Skips fenced code blocks and tables (never wrapped here); merges paragraph/list-item/blockquote continuation lines back to one line each.
- **Two real bugs found and fixed before applying repo-wide**, both caught by testing on real content rather than trusting the first pass:
  - A line ending in a bare hyphen or slash immediately after a letter (e.g. `blast-` / `radius`, `Chrome/` / `Edge`) is a compound word or path split at the wrap point, not this repo's usual spaced `" - "` dash — naive space-joining produced `blast- radius` and `Chrome/ Edge`. Also needed for a trailing underscore (`test_hash_uses_argon2id_` / `variant`, a split identifier).
  - The space still has to survive when the *next* segment also starts with the same connector — `COPY scripts/` / `/app/scripts/` are two separate path arguments, not one path; naively suppressing the space there would have produced `scripts//app/scripts/`. Fixed by only suppressing the space when the next segment starts with a letter/digit, not another connector.
  - Verified before applying: whitespace-normalized diff (fenced code compared byte-for-byte separately from prose) across all 67 files came back with zero unexpected differences — every actual change was either an intentional connector-space removal or the expected collapse of repeated `>` blockquote continuation markers into one.
  - One further miss found by hand after applying: `CLAUDE.md` had one continuation line starting with a literal `+` ("short pitch\n  + pointer into...") that the script's bullet-detector mistook for a new nested list item (`+` is a valid CommonMark bullet marker) and left unmerged — fixed directly, single line, not worth a third script pass for one instance.
- **New CLAUDE.md rule** (Documentation layout section): no hard-wrapping prose going forward — one paragraph/item per line, let the viewer soft-wrap. Documents why (measured char cost, weakened diff-locality argument) so this doesn't drift back in.
- Re-verified after applying: `tools/documentation_checks/run.py` clean (0 broken links, 0 missing `TODO.md`s, 0 oversized stub READMEs), `app/tests` 53 passed. `server/tests` not re-run — doc-only.
- **Doc size**: 69 tracked `.md` files, 314,528 → 310,739 characters (**-3,789, 1.2%**) across this entry and the CLAUDE.md rule addition combined.

## 2026-07-19T04:22:38+00:00 — script the mechanical half of a CLEANING.md pass: tools/documentation_checks/

Joakim asked, after the second cleaning pass this session, for the routines it used to be scripted and checked in so future sessions run them the same way instead of re-deriving them — the dead-link sweep had just been rewritten from scratch, ad hoc, as an inline Python heredoc, twice in one session.

- **New**: `tools/documentation_checks/` (`checks.py` pure logic, `test_checks.py` — 12 tests, TDD'd failing-first before implementation, `run.py` CLI). Covers the mechanical subset of CLEANING.md's methodology: the dead-link sweep, and the "every topic folder has a `TODO.md`" / "code dirs stay one-line stubs"  structural checks. Does **not** cover reading every doc in full, cross-checking claims against code, or judging redundancy — those still need real comprehension, by a person or an AI session, not a script; documented explicitly in the new doc so a future session doesn't mistake "checks pass" for "the pass is done."
  - `find_topic_folders_missing_todo`'s exemption list (`policies`, `bugs/solved`, `bugs/claude` — pure-reference/archive folders with no backlog of their own) lives in `run.py`, not baked into `checks.py`'s logic, since which folders qualify is a judgment call a script can't make alone — same pattern `doc_metrics/log.py` already uses for config the pure-logic module shouldn't own.
  - `find_non_stub_code_readmes` is a soft, size-based heuristic (warns past 400 chars, doesn't fail the run) — a length threshold can signal real content crept into a stub but can't prove it either way.
  - Ran clean against the real repo: 0 broken links, 0 topic folders missing `TODO.md`, 0 oversized code-dir READMEs — matches every manual check from the pass earlier this session.
  - New file `documentation/tooling/DOCUMENTATION_CHECKS.md` (purpose, what's and isn't covered, usage), stub `tools/documentation_checks/README.md` pointing at it, `tooling/README.md`'s contents table updated.
  - `CLEANING.md`'s own step 3 updated from "not currently checked into `tools/`" to point at the new script — closes the gap that file itself had been flagging since it was written this session.
- `app/tests` run clean (53 passed) after this change; `server/tests` not re-run (no `server/`/`app/` code touched — same scoped-rule reasoning as the entry below).
- **Doc size**: `documentation/tooling/DOCUMENTATION_CHECKS.md`: 2,632 chars (new). `documentation/tooling/CLEANING.md` 3,383 → 3,732 (+349). `documentation/tooling/README.md` 4,073 → 4,301 (+228). `tools/documentation_checks/README.md`: 246 chars (new).

## 2026-07-19T04:11:00+00:00 — second documentation-cleaning pass: a cross-branch drift, a stale caveat's ordering, a checklist row left behind by an earlier fix

Joakim asked for another full pass over `documentation/` (a fresh session, scoped via `AskUserQuestion` to CLEANING.md's own on-demand audit process rather than the picture-cleaning-workflow docs). Read every file under `documentation/` in full, ran a dead-link sweep, and cross-checked claims against the actual code (routes, schema, config, JS) rather than trusting prose. Three real findings, all fixed:

- **Cross-branch file-path drift**: `picture-handling/README.md`'s "What exists today" lists `app/utils/directory_picker.py`, `app/gpsdata.py`, etc. — none of which exist anywhere in this branch's `app/` (confirmed via `find`), because `mamma-photo-viewer` is an orphan branch with no shared history with `master`, where those files actually live (confirmed via `git ls-tree origin/master`). A reader on this branch following that section would go looking for files that were never here. Added a note pointing at `master` and at this branch's own (unrelated) `app/` — the GUI code — instead.
- **Caveat ordering**: `gui/README.md`'s "Run it" section states the `docker compose up -d` command before the note that it currently crashes (`MissingConfigError`, stale `JWT_SECRET_KEY`-less compose file) — the earlier same-day pass (entry below) added that caveat "next to" the instructions, but "next to" still meant *after* the command a reader would copy first. Reordered so the warning reads before the command.
- **Checklist row left stale by its own referenced rule**: `tooling/README.md`'s wrap-up checklist had "Full test suite | before every commit | local" as one row — but the actual rule (CHANGELOG 2026-07-19T03:53:21+00:00, decided *after* the prior cleaning pass below) scopes `server/tests` to skip re-running against unchanged code for a doc-only commit. Split into two rows matching `app/tests` vs `server/tests`'s real, different trigger conditions, same granularity the table's other rows already use.
- **Checked clean, no changes needed**: zero broken relative links across all 67 git-tracked `.md` files (dead-link sweep before and after); `DATA_DICTIONARY.md`'s "only `users`/`audit_log` exist" claim confirmed against `server/app/db.py`; Phase 2+ "not built" claim confirmed (no `/tags`/`/photos`/`/catalogues` routes exist); `DEFERRED.md`'s 5-minute access-token TTL confirmed against `server/app/tokens.py`; Swagger lockdown (`docs_url=None` etc.) confirmed in both `server/app/main.py` and `app/main.py`; `gui/README.md`'s "53 tests" claim confirmed via `pytest --collect-only`; `file-integrity/TODO.md`'s `.mkv`/`.webm` signature-check gap confirmed against `app/main.py`'s `VIDEO_EXTS` vs `_EXPECTED_LABEL_FOR_EXT`; every `bugs/reports/*.md` file has its promised `Status:` line; structural convention compliance (stub-only code-dir READMEs, every topic folder's `TODO.md`, nothing project-wide duplicated outside `POLICY.md`) all held.
- **Found, deliberately not fixed**: this file's own `(6)` entry below states "82 `.md` files in the repo" at the time of that pass; the actual git-tracked count, both then (per that entry's own dead-link sweep) and now, doesn't reconcile with today's confirmed 67 — most likely the same class of unfiltered-walk pollution `DOC_METRICS.md` already documents fixing once (vendored `.md` files under a gitignored directory inflating a naive `rglob`-based count), but not confirmed, and fixing the number would mean editing an already-published entry. Flagging for Joakim's call rather than silently editing history.
- `app/tests` run clean (53 passed) after the doc-only edits; `server/tests` not re-run — no `server/`/`app/` code changed this session, so the newly-clarified checklist row above doesn't call for it.
- **Doc size**: `documentation/picture-handling/README.md` 1,062 → 1,486 (+424). `documentation/gui/README.md` 7,842 → 7,923 (+81). `documentation/tooling/README.md` 3,854 → 4,073 (+219).

## 2026-07-19T04:00:36+00:00 — document today's documentation-cleaning pass as a reusable, on-demand routine

Joakim asked for the goals behind today's audit to be written down as a standing routine for "this kind of cleaning job" — explicitly not in CLAUDE.md, since it isn't something every session needs to run.

- **New file** `documentation/tooling/CLEANING.md`: the goals (reduce a fresh session's ramp-up time and token cost without losing context, via thorough/precise auditing rather than just brevity), the methodology actually used today (read everything in full, cross-check against code not just other docs, dead-link sweep, structural convention compliance, fix-vs-flag judgment calls, verify before committing), and a pointer back to today's `(6)` entry as the concrete precedent. Placed as a peer to `COMMIT_COST.md`/`DOC_METRICS.md` (recommended over a new `tooling/cleaning/` subfolder + mandatory `TODO.md` — those two established tools don't get their own subfolders either, and this isn't an ongoing topic with its own backlog).
- `tooling/README.md`'s contents table updated to list it.
- **Doc size**: `documentation/tooling/CLEANING.md`: 3,401 chars (new). `documentation/tooling/README.md` 3,754 → 3,874 chars (+120).

## 2026-07-19T03:54:48+00:00 — session wrap-up: commit_cost's known boundary bug reproduced live

While logging commit_cost for the previous entry, noticed this session's own commits from `f69979d` onward were logging as "human-only, 0 tokens" despite being AI-authored — the exact known bug in `bugs/reports/2026-07-17-commit-cost-boundary-detection-breaks-on-long-sessions.md`. Logged the fresh reproduction there (same shape as the original: a real prefix, then a hard cutoff, nothing after).

- That bug file already establishes its own recurrence as a practical "this session has run long enough" signal, not just a tooling bug — taking that at face value rather than continuing to add more work this session.
- **Doc size**: `bugs/reports/2026-07-17-commit-cost-boundary-...md` 2,638 → 3,523 chars (+885).

## 2026-07-19T03:53:21+00:00 — scope the full-test-suite-every-commit rule: skip a redundant server/tests re-run

Joakim caught it live: the container-based `server/tests` suite had just been run twice in a row against completely unchanged server code (the two prior entries below were doc-only), each run guaranteed to pass before it started — pure cost (Docker container spin-up, a permission prompt) for zero new information.

- **Rule scoped**: `app/tests` (fast, in-process) still runs before every commit, docs-only or not. `server/tests` (container-based) now only re-runs for a doc-only commit if it hasn't already run clean this session against the same, unchanged `server/`/`app/` code — otherwise it's mandatory the moment code changes again. Applied immediately to this very commit: only `app/tests` ran, since `server/tests` already ran clean twice already this session with nothing in between to invalidate it.
- **Doc size**: `CLAUDE.md` 14,828 → 15,151 chars (+323).

## 2026-07-19T03:50:56+00:00 — trim CLAUDE.md's recurring accumulated-detail pattern; add a "starting a session" pointer

Joakim asked why CLAUDE.md was 251 lines when he'd expected mostly pointers, and why sessions need 3-5 correction messages before they're oriented. Both had concrete answers.

- **Accumulated detail, again**: the TDD, "never claim an action taken," and "promised follow-up" bullets each carried a full inline incident narrative — the exact pattern a 2026-07-17 pass already caught and partly fixed once. Two of the three already linked to a `bugs/claude/*.md` file that had the same story; trimmed both to rule + pointer. The TDD bullet had no such file at all, which is itself a gap against the "every lapse is its own file" hard rule — backfilled `bugs/claude/2026-07-19-skipped-tdd-for-a-small-helper-reasoning-it-wouldn-t-matter.md` with the narrative, then trimmed CLAUDE.md's bullet to match the other two.
- **New "Starting a session" section**: CLAUDE.md is the one file guaranteed to auto-load; everything else (status, open bugs, TODO progress) only gets read if a session goes looking. CLAUDE.md deliberately holds rules, not status, so a fresh session had nothing telling it to go find that status before acting. Added a short pointer at the top: read `documentation/README.md`'s index, then the relevant topic's `Status:` line, before assuming current state.
- Doc-only change; full local test sweep: 53 `app/tests` + 49 `server/tests`, all green.
- **Doc size**: `CLAUDE.md` 15,707 → 14,828 chars (-879 net — the three trims outweighed the new section). New file `bugs/claude/2026-07-19-skipped-tdd-for-a-small-helper-...md`: 1,673 chars.

## 2026-07-19T03:42:35+00:00 — adopt timestamped changelog headings, drop the same-day counter

Follow-up to the documentation audit two entries below: that audit found this file's own 2026-07-19 block had two entries both labeled `(3)`, caused by two concurrent conversation threads each keeping an independent same-day counter with no way to see what number the other had already used. Deliberately left unfixed at the time (fixing it meant editing already-published entries, against this file's own never-rewrite rule) — Joakim asked for the actual convention change instead.

- **Changed**: new entries now head with a UTC ISO 8601 timestamp instead of an incrementing `(N)`. First tried a bare local `HH:MM`; Joakim pointed out that's still coarse enough to collide within the same minute and leaves the timezone implicit. Switched to `datetime.now(timezone.utc).isoformat(timespec="seconds")` — second-precision, explicit UTC, and not a new format at all: it's the exact convention `tools/doc_metrics/log.py` and `tools/commit_cost/log.py` already use for their `recorded_at` field, so the repo now has one timestamp convention instead of two. A timestamp needs no coordination with what a different, concurrent session already wrote, which is exactly the coordination that broke down. Documented in [CLAUDE.md](CLAUDE.md)'s changelog rule; this file's own header now explains where the old convention stops and the new one starts, so a reader isn't left guessing why the heading format changes partway through the file.
- **Not changed**: no past entries were renumbered or reheaded, including the duplicate `(3)` — that stays as a permanent, visible record of why this convention exists, rather than being quietly smoothed over.
- Doc-only change (two files); full local test sweep still run per this project's "even docs-only edits" rule: 53 `app/tests` + 49 `server/tests`, all green (unaffected, as expected).
- **Doc size**: `CLAUDE.md` 15,240 → 15,707 chars (+467). This file: 47,773 → ~50,300 chars (this entry, approximate — this line's own length feeds back into the count it's reporting).

## 2026-07-19 (6) — full documentation audit: dead facts, a stale index, a lost root pitch

Joakim asked for a thorough pass over every doc in `documentation/` against the guidelines and against the actual code, aimed at cutting a fresh session's ramp-up time/tokens without losing context. Ran three parallel research agents (bugs+tooling, photo-server+architecture, policy+cross-links) plus a full-repo dead-link sweep, then fixed everything that was a clear-cut factual error or contradiction.

- **Bug tracking**: the thumbnail silent-refresh bug (already fixed 2026-07-19 per entry (2) below) was still listed open in `photo-server/README.md` and its own report's `Status:` line — moved to `bugs/solved/` via `mark_solved.sh` and both updated. Also removed a dead instruction ("remove the entry from `bugs/TODO.md`") from `bugs/solved/README.md` and `mark_solved.sh`'s own printed output — `bugs/TODO.md` keeps no per-bug index (deliberately dropped 2026-07-17), so the instruction referred to a convention that no longer exists.
- **Stale facts contradicting code**: access-token TTL corrected from "15 min" to the actual 5 min (`server/app/tokens.py`) in three spots in `photo-server/TODO.md`; `gui/TODO.md` called `app/` "Flask" — it's FastAPI, contradicting `gui/README.md`'s own correct line one file over.
- **Missing caveat**: `gui/README.md`'s "Run it" instructions didn't mention that the repo-root `docker-compose.yml` is stale and will crash on a missing `JWT_SECRET_KEY` — that fact existed only buried in `TODO.md`'s dated session log. Added next to the instructions themselves.
- **Doc index and status drift**: `documentation/README.md`'s top-level folder table was missing `bugs/`, `file-integrity/`, and `gui/` entirely (the last being where this branch's whole feature lives) and had `picture-handling/`/`photo-server/` backwards (calling the superseded single-machine tool "current work"). Fixed the table and `picture-handling/README.md`'s own stale "current phase" claim. `photo-server/README.md`'s Status line and open-problems list were a day stale (missing the 07-19 redeploy and the new picture-click-failed bug) — updated.
- **Root README.md**: on this branch it had been fully overwritten with branch-specific content, losing the general project pitch CLAUDE.md describes this file as ("public-facing landing page"). Restored the pitch (matching `master`) with a branch-specific pointer section added underneath; fixed `gui/README.md`'s claim that the branch-only stub was "per this repo's doc-layout convention" (it wasn't — that convention is for code-directory READMEs, not the root one).
- **DATA_DICTIONARY.md**: its "'now' = built" framing read as "already exists in the database" when only `users`/`audit_log` actually do (`db.py`'s `ensure_schema()`) — Phase 2's tables are designed, not built. Reworded the definition and added an explicit today-status note. Also reattached an "Ownership" row that had drifted ~25 lines below the table it belonged to.
- **Redundant/undocumented mechanics**: trimmed `create_bug_report.sh`'s `--claude` template, which hardcoded a near-verbatim restatement of `bugs/claude/README.md`'s own opening paragraph into every future file; added the missing `## What changed` section to `2026-07-17-claude-md-accumulating-detail-...md` (the one file that didn't comply with `bugs/claude/README.md`'s own hard rule); documented `check_coverage.sh` in `COMMIT_COST.md` (referenced from three other places, never explained there); stated the closed-by-default privacy rule explicitly in `POLICY.md` itself (previously only asserted independently in `photo-server/README.md` and presupposed by `VISION.md`, inverted from this project's own "nothing project-wide duplicated outside POLICY.md" rule) and pointed both `photo-server/README.md` and `DATA_DICTIONARY.md`'s GPS/EXIF-log line at it instead of restating.
- **Found, deliberately not fixed**: `CHANGELOG.md`'s own 2026-07-19 entries have a duplicate `(3)` label (this file's own entries (2)-(5) are internally consistent — cross-referenced against each other and correct — but two entries below share the number `(3)`, and there are two unnumbered entries instead of the usual single oldest-of-the-day). Left untouched: fixing entry *labels* still means editing already-published CHANGELOG entries, and this file's own rule is "never rewrite or reorder past entries" — flagging for Joakim's call rather than silently editing history, even for a numbering-only fix.
- **Checked clean, no changes needed**: zero broken relative links across all 82 `.md` files in the repo (full sweep, both before and after these edits); no circular/non-terminating cross-references anywhere; `DEPLOYMENT.md`/`HARDWARE.md`/`TOOLCHAIN.md`/file-integrity docs all match code; `DOC_METRICS.md`/`COMMIT_COST.md`'s documented CLI flags match the actual argparse code exactly; the MySQL-vs-Postgres drift flagged in `picture-handling/TODO.md` is still accurate, not stale.
- Full local test sweep after the doc-only changes (two shell scripts touched, no app code): 53 `app/tests` + 49 `server/tests`, all green.
- **Doc size**: `README.md` 261 → 963 (+702, restored pitch + branch pointer). `documentation/README.md` 733 → 1,038 (+305, index fixed). `documentation/photo-server/DATA_DICTIONARY.md` 6,105 → 6,538 (+433). `documentation/photo-server/README.md` 6,162 → 6,221 (+59). `documentation/photo-server/TODO.md` 38,870 → 38,867 (-3, TTL fixes). `documentation/gui/README.md` 7,427 → 7,893 (+466). `documentation/gui/TODO.md` 17,110 → 17,112 (+2). `documentation/picture-handling/README.md` 878 → 1,066 (+188). `documentation/policies/POLICY.md` 6,006 → 6,372 (+366). `documentation/tooling/COMMIT_COST.md` 5,417 → 5,922 (+505). `documentation/bugs/solved/README.md` 815 → 668 (-147, dead instruction removed). `documentation/bugs/claude/2026-07-17-claude-md-accumulating-detail-...md` 2,865 → 3,234 (+369). New file `documentation/bugs/solved/2026-07-18-thumbnail-img-tags-...-SOLVED.md`: 4,157 chars (moved + updated from `bugs/reports/`).

## 2026-07-19 (5) — confirmed the `Bash(*)`-still-prompts pattern is an upstream Claude Code bug; consolidated CLAUDE.md

Continuation of this same day's permission-prompt investigation (see the 07-19 entry below, two below this one). That entry's conclusion — "two distinct causes, `Bash(*)` works correctly for ordinary in-repo commands" — was too narrow: Joakim then showed plain, already-allowlisted `git status`/`git commit`/`git push` prompting in other windows, with no `cd`-prefix and no outside-repo read involved, ruling that conclusion out as the full explanation.

- **Searched for prior reports before filing anything new** (per this project's "ask or search" rule): found [claude-code#20449](https://github.com/anthropics/claude-code/issues/20449) — the canonical upstream issue (three other reports closed into it as duplicates), confirmed reproducing in the VS Code extension specifically, including a bare `git add` prompting despite overlapping allow patterns, as late as 2026-05-17. This is the real explanation for the original "almost every session" complaint — not a config gap on this repo's side.
- **Attempted to add our specific evidence as a comment** (`Bash(*)` — the broadest possible wildcard — still not fully reliable, plus the same-session inconsistency: one window ran plain `git status`/`git log` silently while others didn't). **Failed**: the issue was auto-locked after 7 days of post-closure inactivity; GitHub rejects new comments on it from anyone. Filing a fresh issue referencing #20449 is the only remaining path, not done yet — Joakim's call whether/when.
- **Also traced, live in this session, why "four windows" happened today**: not the duplicate-session VS Code bug — that theory was already corrected in the entry above (edited/re-sent prompts fork a new tab, expected behavior) — but a red herring for the *original* complaint regardless, since Joakim confirmed the prompt frequency doesn't depend on session count; #20449 is the actual cause.
- **CLAUDE.md consolidated**: the "never read outside this repo" bullet added earlier today duplicated "Known, accepted permission popups" in spirit (both are Claude-Code-level hardcoded floors no setting can suppress) but lived in a separate, disconnected part of the file — against this file's own "lean, no restating elsewhere" rule. Merged into that section as a second bullet alongside the Docker floor, and added a third bullet there pointing at #20449 so a future session doesn't re-diagnose this from scratch.
- **Doc size**: `CLAUDE.md` 14,892 → 15,240 chars (+348, net of removing the standalone bullet and folding it into the existing section with more detail). This file: 38,720 → 41,558 chars (+2,838, this entry).

## 2026-07-19 (4) — session wrap-up: corrected a stale root-cause theory, opened one live bug

Closing out a very large session (single-album view through idle timeout - see entries (1)-(3) below). This entry is the wrap-up sweep itself, plus one correction that surfaced during it.

- **Corrected a 2-day-old wrong root-cause theory**: the "why this project lives in this repo" history note (both here implicitly and in `gui/TODO.md`) attributed a duplicate-Claude-Code-session incident to a suspected VS Code extension bug (typing during a popup). Joakim identified the real cause: editing/changing a previously-sent prompt forks the conversation into a new tab - expected behavior, not a bug - which only looked alarming because both tabs' sessions shared the same working tree. Corrected in `gui/TODO.md` and in this session's own cross-session memory file (kept the superseded theory visible rather than deleted, for context).
- **Opened, not closed**: a live "picture click failed to show" report (`bugs/reports/2026-07-19-picture-click-failed...md`) - investigation ongoing, root cause not yet confirmed (ruled out a session-wide token issue; still need the exact failed request's status code from DevTools). Filed later than it should have been - see the paired process-lapse report, `bugs/claude/2026-07-19-didn-t-create-bug-report-at-investigation-open...md`.
- **Docker hygiene**: no dangling images. Stopped `photo_server_test_pg`/ `_redis` (the disposable server-side test fixtures) at session close, after re-confirming the full `server/tests` suite passes with them up.
- **commit_cost coverage**: clean (`check_coverage.sh`'s one "missing" entry is always the just-made commit, per its own documented caveat - not a real gap).
- **Forward-effectiveness note**: this session ran very long and covered many distinct threads in quick succession (album display, DOM weight, sticky-header CSS, a dead feature removal, two live-bug fixes, a new cross-session logging routine, a stale root-cause correction) with several genuine mid-session pivots. The thing that kept it coherent rather than lossy was routing every real decision point through `AskUserQuestion` instead of running text - caught and corrected once early on, held for the rest of the session. Next session: keep doing that from the start, especially in a session this topically wide, rather than needing the same correction again.
- **Doc size**: `documentation/gui/TODO.md` 16,870 → 17,110 chars (+240, the root-cause correction).

## 2026-07-19 (3) — idle timeout for the new silent-refresh keep-alive

Joakim caught a real side effect of the entry below's fix immediately after it shipped: proactively refreshing the session cookie every 4 minutes means a browser tab left open indefinitely - genuinely unattended, not just idle within a browsing session - now stays logged in forever, with no timeout at all.

- **Fixed**: `app.js` tracks real user activity (mouse move/keydown/click/scroll/touch), and `silentRefresh()` now skips its proactive `/refresh` call once 30 minutes have passed with none. Not an abrupt forced logout - it just stops the new mechanism from artificially extending a session past the existing 5-minute access-token / 12-hour refresh-token lifetimes, restoring the bound that already existed before today's fix.
- **New Selenium test**: confirms zero `/refresh` calls fire once idle (via `?test_idle_ms`, tiny for the test), written and confirmed red before the fix. 8 Selenium + 53 `app/tests` + 49 `server/tests`, all green after.
- **Doc size**: `documentation/gui/TODO.md` 16,130 → 16,870 chars (+740).

## 2026-07-19 (2) — real-library feedback: DOM-unload inactive albums, fix sticky-header overlap

Follow-up to the entry below, after deploying to production and testing against Joakim's actual 16-album library instead of 3 fake test albums. Two real bugs surfaced that the smaller local fixture hadn't caught.

- **Inactive albums no longer exist in the DOM at all** — the previous version still built every album's markup (including thumbnail `<img>` tags) and only hid the inactive ones with CSS. Joakim correctly flagged this as real, unnecessary weight at library scale, not just a visibility question. `app.js`'s `renderTree()`/`renderActiveAlbum()` now build only the active album's DOM; `setActiveAlbum()` tears it down and rebuilds on switch. `allImages` (used by the lightbox and "download all", which intentionally still span every album per the entry below) is now computed as a flat list up front from the raw tree data, decoupled from DOM construction, so hidden albums cost nothing while global next/prev and download-all still work.
- **Fixed sticky pill-bar overlap on scroll**: `#toolbar` and `#albumNavBar` were two independently `position: sticky` elements, the pill bar hardcoded to `top: 3.6rem` assuming a toolbar height that didn't match reality (measured 111.78px vs. the assumed 57.6px against the real page). Fixed by wrapping both in one `#stickyHeader` container that alone is sticky - no offset to keep in sync, ever.
- **New Selenium tests**: DOM-absence assertions (not just "hidden" class) for inactive albums, and a `getBoundingClientRect()`-based overlap check after scrolling - both written and confirmed red against the two bugs above before fixing them. 6 Selenium + 53 `app/tests` + 49 `server/tests`, all green after.
- **Debugging note**: diagnosed live via a JS snippet run in Joakim's actual browser console (Firefox), not just screenshots - confirmed the DOM state directly rather than guessing from visual description. Firefox's paste-guard needed an actual paste attempt before typing "allow pasting" would work; logged as its own note for next time.
- **Logged, not built**: Joakim asked to consider Bootstrap/jQuery (or similar) instead of the current no-framework/no-build-step stack, and a CSS reset/normalize library - captured in `gui/TODO.md`, explicitly deferred, not evaluated this session. Also logged, also not built: a bigger redesign reframing folder-path segments as tags/sub-tags with the per-album header removed entirely - genuinely open on where sub-tags live in the UI, needs its own design pass.
- **Removed entirely**: "Markera som klar" (per-album visited toggle + toolbar counter) and "Dölj" (per-album collapse). Both were designed for the old all-albums-stacked layout; asked about relocating them once the header row was on the chopping block, Joakim didn't recall their purpose, and on finding out "Dölj" specifically had none left once only one album is ever shown at all, asked to delete both outright - `app.js`, `index.html`, and `style.css` all cleaned of the supporting code, not just the buttons.
- **Fixed thumbnails breaking on token expiry, without ever needing a reload**: the already-known bug (`bugs/reports/2026-07-18-thumbnail-img-tags-have-no-silent-refresh-on-expired-access-token.md`) went from "a mechanism that exists" to confirmed live during this session (Joakim hit it in normal browsing, no restart involved) - "just reload" turned out not to be a real workaround either (the folder-picker permission doesn't reliably survive a reload, plus lost scroll position). Fixed with the standard "silent refresh" pattern - confirmed against external sources before building, not guessed: a proactive `setInterval` in `app.js` (`silentRefresh()`, every 4 minutes, under the 5-minute access-token expiry) calls `/refresh` the entire time the gallery is open, so the session cookie plain `<img src>` thumbnail/lightbox loads depend on never actually goes stale in normal use. `?test_refresh_ms` overrides the interval for the new Selenium test, which can't wait out the real 4 minutes.
- **Doc size**: `documentation/gui/README.md` 6,886 → 7,427 chars (+541). `documentation/gui/TODO.md` 11,422 → 16,130 chars (+4,708). `bugs/reports/2026-07-18-thumbnail-img-tags-...md` 2,915 → 3,944 (+1,029, real-world-frequency confirmation). New file `bugs/claude/2026-07-19-asked-inline-instead-of-using-askuserquestion-...md`: 2,138 chars.

## 2026-07-19 — single-album view + a minimal Selenium test suite

Joakim asked to make sure the GUI is up and running, plus change album display to show only one at a time with easy, well-tested switching.

- **Single-album view shipped**: `app.js`'s nav-pill bar now switches which album is shown (`setActiveAlbum()`) instead of scrolling to it; all other albums are hidden. Choice persists across reloads via `localStorage` (`mpv_active_headline`). "Download all" and the lightbox's prev/next intentionally still span every album (unchanged, flagged in TODO.md as a separate future decision, not silently changed alongside the display switch).
- **New Selenium test infra** (`scripts/test_selenium.sh`, `app/tests_selenium/`): first real build-out of the Selenium direction decided 2026-07-18 but never started. Runs a disposable `selenium/standalone-chrome` container (`--network host`) against a real `uvicorn` process started directly from `.venv-test`, with a throwaway multi-album photo tree and a manually-signed JWT cookie (bypasses the real login flow, which needs Postgres/Redis this suite doesn't run). 4 new browser-level tests, all TDD (written and confirmed red against the old scroll-based behavior before the fix). Full local test sweep after the change: 4 Selenium + 53 `app/tests` + 49 `server/tests`, all green.
- **Found while checking "is the GUI up": the root `docker-compose.yml` (this dev workstation, not production) is stale** — predates `app/auth.py`'s login requirement (commit `9c090b0`, 2026-07-17) by about 15 hours, so a rebuild here would crash on startup (`MissingConfigError`, missing `JWT_SECRET_KEY`). The one container that ever ran on this machine did so for a few hours the night before that commit and has sat `Exited` since — not evidence of an ongoing local workflow, as it first appeared. Confirmed the actual live system is production only (`https://photos.reuterborg.se`, kept current by push-here/pull-and-rebuild on `192.168.1.10` per `DEPLOYMENT.md`) - reachable and returning `200` as of this session. Not fixed this session (no local full-stack dev environment exists yet); written up in `documentation/gui/TODO.md`'s new 2026-07-19 section rather than left only in this chat.
- **Doc size**: `documentation/gui/README.md` 6,012 → 6,886 chars (+874, features + testing sections updated), `documentation/gui/TODO.md` 9,144 → 11,422 chars (+2,278, Selenium bullet updated + new session section).

## 2026-07-19 — resolved the 07-17 `Bash(*)`-still-prompts anomaly; hardened the no-outside-repo-access rule

Joakim reported still getting popups "almost every session" despite `Bash(*)` and global `defaultMode: "auto"` already being set. Tested live in-session: plain `git status --short`, `&&`-chained, and piped through `grep` (including the exact secrets-scan pattern from the pre-commit routine) all ran silently — `Bash(*)` works correctly for ordinary in-repo commands. Isolated two real, distinct causes instead:

- **A `cd <repo-path> && git ...` prefix triggers a prompt even when the path is the current directory** — this resolves the 07-17 entry's unresolved `git -C <path> log ...` anomaly; same mechanism, an explicit path argument on/before a git invocation re-triggers directory-access scrutiny that a bare command (relying on the shell's already-known cwd) doesn't. This is a Claude-session habit to avoid (per the Bash tool's own instructions: never prepend `cd <current-directory>` to a git command), not a `.claude/settings.json` gap.
- **Commands reading outside the repo tree** (`find /`, `npm ls -g`) independently prompt regardless of `Bash(*)` — directory access is a separate permission dimension from command-pattern matching, confirmed again here on top of the 07-17 finding.
- Offered widening `permissions.additionalDirectories` to cover cross-project/global reads; Joakim rejected this firmly and asked for the boundary to be *harder* to accidentally cross, not softer — wrote this as an explicit non-negotiable in CLAUDE.md rather than leaving it as an in-chat preference (see CLAUDE.md's new outside-repo-access rule).
- Also traced Joakim's recollection of a Docker/`sudo` permission fight to `buzzkit`, not this repo — already resolved and documented there per the 07-17 entry below; this repo's Docker prompts are the separate, unrelated, by-design `docker run`/`rmi`/`volume rm` floor (see CLAUDE.md's "Known, accepted permission popups").

CLAUDE.md: 14,749 → 15,455 chars (+706, new non-negotiable). This file: 23,102 → 27,777 chars (+4,675, this entry).

## 2026-07-19 (3) — trimmed CLAUDE.md duplication into a real wrap-up checklist; logged an ad-hoc-labels lapse

Same day's continuation: a separate conversation about wrap-up cadence found the checklist had grown open-ended enough that ending a session took about as long as the work being closed out (see `bugs/claude/2026-07-18-session-wrap-up-itself-grows-unpredictably-long.md`).

- **CLAUDE.md trimmed**: the three duplication candidates flagged 2026-07-17 (`bugs/claude/2026-07-17-claude-md-accumulating-detail-that-belongs-in-more-specific-docs.md`) are resolved — 2 trimmed to one-line pointers, 1 found already absent (never actually landed, or removed in an earlier undocumented pass). The "not evaluated" push-policy bullet in that file is still open.
- **New wrap-up checklist** in `documentation/tooling/README.md`: every check an AI session should run before calling a session done, each with an explicit trigger condition (most are conditional — "if a manifest changed," "if `docker build` ran" — not blanket-every-session like before, which is what made wrap-up itself slow). Also added: a standing rule to keep flagging drift/session-length plainly in every message once either shows up, not just once.
- **New process-lapse report**: this session referred to two parts of its own reply as "thread 1"/"thread 2" without ever defining the labels in the text — Joakim had to ask what they meant. No new CLAUDE.md rule (existing "lean, exact, self-sufficient" principles already cover it); logged as a behavioral correction instead — see `bugs/claude/2026-07-19-used-unexplained-ad-hoc-labels-instead-of-plain-language.md`.
- **New open items** in `documentation/tooling/TODO.md`: the wrap-up checklist should eventually be code (a script checking each trigger), not prose an AI session has to remember correctly; whether `doc_metrics`/`commit_cost`/the not-yet-built test-ledger should consolidate into one shared database instead of separate `.jsonl` files; a new hard rule against shorthand/abbreviated names going forward (`doc_metrics` itself cited as the example that doesn't parse on sight) — naming an existing rename candidate, not deciding to rename it yet.
- **Doc size**: `CLAUDE.md` 14,743 → 14,892 chars (+149 net — the trimming removed more than the pointers added back). `documentation/tooling/README.md` 580 → 3,754 (+3,174, new checklist). `documentation/tooling/TODO.md` 654 → 2,452 (+1,798, 3 new items). `bugs/claude/2026-07-17-claude-md-accumulating-...md` 2,091 → 2,865 (+774, status update). New file `bugs/claude/2026-07-19-used-unexplained-ad-hoc-labels-...md`: 1,537 chars.

## 2026-07-18 (4) — session wrap-up: doc-drift sweep, loose ends closed

Closing out a very large session (outage, Swagger fix + redeploy, containerization policy, tags design discussion). This entry covers the wrap-up sweep specifically — see entries (1)-(3) below for the session's substantive work.

- **Doc-drift fixed**: `photo-server/README.md`'s status line was still dated 2026-07-17 and pointed at `bugs/TODO.md`'s old priority-list format (removed 2026-07-17/18) — rewritten to reflect today's actual state (production redeployed and current as of commit `a8979c0`, Swagger fix live, three real bugs still open). Same stale `bugs/TODO.md`-as-index pattern fixed in two more places in `photo-server/TODO.md`, and the Postgres-schema/Dockerfile-scripts bugs it referenced as open are now correctly marked solved there too.
- **Loose ends from the chat closed into durable docs**, not just left unanswered: the thumbnail pre-compile design synthesis (worked out from Joakim's answers earlier this session but never actually sent back for confirmation - a real miss, now written into the bug report and flagged as still needing his sign-off before building), the Playwright-vs-Selenium concern (Microsoft ownership, containers-only constraint), the download-folder UX rework, and the grid-pagination idea (new bug report) are all now captured in `gui/TODO.md`/`bugs/reports/` rather than only existing in chat history.
- **Process lapse logged**: told Joakim a `DATA_DICTIONARY.md` edit had been made when it hadn't - caught when he came back to confirm agreement with the graph-DB recommendation and a grep found nothing there. Fixed, logged in `bugs/claude/`.
- **Doc size**: net **+8,377 chars** across 7 files this wrap-up round (6 edited, 1 new) — `gui/TODO.md` +2,441 (largest, the loose-ends consolidation), `pre-compile-thumbnails` bug report +1,827 (the design synthesis), new pagination bug report +1,565, `photo-server/TODO.md` +703, `DEFERRED.md` +579, `README.md` +490.
- **Forward-effectiveness note**: the biggest friction this session wasn't any single bug — it was **claiming an action was taken in the same reply that described it, without a final check against what tool calls actually ran**. It happened at least twice (this session's `DATA_DICTIONARY.md` miss, logged above) across a very long, multi-topic session where replies increasingly bundled several file edits into one message. Next session: in any reply describing more than one doc edit, verify each "logged/added/fixed" claim against the actual tool calls made in that turn before sending - especially once a session has been running long enough that earlier context is easy to misremember as "already done."

## 2026-07-18 (3) — outage root cause found (switch), plus two new live findings

- **Outage resolved**: root cause was the switch between the server and router - it had been running continuously for a couple of years with no reboot. A power cycle restored the link immediately. Not a cable, NIC, or router fault after all - see the outage report's final entry.
- **New finding, same power event**: right after recovery, "no new thumbnails nor pictures loading" turned out to be an auth problem, not a thumbnail-generation one - `redis` has no persistent volume in `docker-compose.prod.yml`, so the restart wiped every active session's refresh token. Fresh login unblocks it immediately; the real fix (give Redis a persistent volume) isn't built yet - see `documentation/bugs/reports/2026-07-18-redis-has-no-persistent-volume-every-restart-wipes-active-sessions.md`.
- **Related but distinct finding**: grid thumbnails and the lightbox's full-size image are plain `<img>` tags, which bypass `app.js`'s only 401-silent-refresh path (`authFetch`, used solely by `fetch()`-based calls). This means an access token's normal 5-minute expiry alone, with no restart involved, could break thumbnails mid-browsing-session
  - not yet confirmed happening outside today's Redis-restart incident, but the code path clearly allows it. See `documentation/bugs/reports/2026-07-18-thumbnail-img-tags-have-no-silent-refresh-on-expired-access-token.md`.
- **Also opened**: a lightbox bug (popup shows the previous photo when clicking a not-yet-loaded thumbnail) - investigation not yet conclusive, needs a live repro session rather than more code reading.
- **New tooling backlog item**: `documentation/tooling/TODO.md` (new - that folder previously claimed "no open work", no longer true) - a compact per-run test-result ledger, same shape as `doc_metrics`/ `commit_cost`. Explicitly distinguished from what `documentation/bugs/reports/`'s investigation logs already do (capture debugging *reasoning* for a future session, not test pass/fail trends) - the two aren't a substitute for each other.

## 2026-07-18 (2) — live outage investigation, new "document as you go" policy

- **`photos.reuterborg.se` unreachable**: found mid-session. DNS and public IP both confirmed correct (not the cause) — the server (`192.168.1.10`) isn't answering at the LAN network layer at all (`ip neigh` `INCOMPLETE`, no route to host on 22/80/443), despite Joakim confirming it's powered on with the cable seated. Full investigation log, leading theory, and next step in `documentation/bugs/reports/2026-07-18-photos-reuterborg-se-unreachable.md` — **status: investigating, not fixed**, awaiting output from directly on the server.
- **New CLAUDE.md policy**: bug/incident files now get created at investigation-*open*, not fix-time — via `tools/new_bug_report/new_bug_report.sh`, updated as findings come in. Applied to this very outage as the first case. Replaces a now-stale bullet that referenced `bugs/TODO.md`'s old index (removed 2026-07-17/18). **Doc size**: CLAUDE.md +110 chars (net: fixed a stale reference, added the new policy); new bug report file 3,230 chars.

## 2026-07-18 — real fixes for the two deploy-path bugs (schema init, missing scripts/)

- **Postgres schema init**: `server/app/main.py` now calls `ensure_schema()` from a FastAPI `lifespan` handler on every `auth` container startup (idempotent, so safe on restart) — no more manual one-off `python -c` step after a fresh deploy. TDD'd via `tests/test_main_startup.py` (mocks `get_connection`/`ensure_schema`, asserts the lifespan handler calls them).
- **`server/Dockerfile` missing `scripts/`**: added `COPY scripts/ /app/scripts/` to both build stages, so `python -m scripts.create_account` works as originally documented instead of the inline-`python -c` workaround. TDD'd via a new `tests/test_dockerfile_build.py` (`@pytest.mark.docker`, builds the real image and execs an import inside it) — the first test in this repo that builds/runs a Docker image rather than importing the source tree directly; documented as the standard pattern for future `Dockerfile` changes in `documentation/photo-server/TOOLCHAIN.md`. Excluded from the default `uv run pytest tests` run (`pyproject.toml`'s `addopts = "-m 'not docker'"`, too slow to pay on every run) — run explicitly with `-m docker` when `Dockerfile` changes.
- Both bugs moved to `documentation/bugs/solved/`; `documentation/photo-server/DEPLOYMENT.md` steps 4-5 updated to drop the now-obsolete workarounds.
- **Doc size**: `documentation/` net **+1,367 chars** (codepoints) across the 4 files touched — `DEPLOYMENT.md` -443 (workarounds removed), `TOOLCHAIN.md` +1,091 (new Dockerfile-testing section), the two now-`solved/` bug reports +307 and +412 (real-fix writeups replacing "not built yet" stubs).

## 2026-07-17 (5) — bugs/ tracking overhaul, live thumbnail fixes

- **Live production fix**: photo-viewer was being hard-killed shortly after serving `/thumb` requests (app down for Elisabeth). Raised `mem_limit` 256m->512m, added a `MAX_CONCURRENT_THUMBNAILS` semaphore around thumbnail generation (TDD'd), and used `Image.draft()` to skip full-resolution JPEG decode for thumbnails (TDD'd) — all three deployed, confirmed stable for 2+ hours (previously restarting every few minutes). Remaining latency is per-image on-demand generation time, not a crash — logged as the next real fix (pre-compile ahead of time, Joakim's direction).
- **`bugs/` restructured, hard rule**: every bug and every AI-session process lapse is now its own dated file (`bugs/reports/`, `bugs/claude/`) — never a bullet in a shared list. `TODO.md`/`LOG.md` are pure indexes now. New `bugs/solved/` archive for genuinely resolved reports (`tools/new_bug_report/mark_solved.sh`). New `tools/commit_cost/check_coverage.sh` compares `git log` against `commit_costs.jsonl` and reports gaps — added after 3 commits went out mid-session without their required cost-logging step, unnoticed until asked about directly. Both wired into CLAUDE.md's wrap-up routine.
- **Found live**: `tools/commit_cost`'s boundary-detection stops working partway through one long session (only matched the first ~40% of this session's commits) — real spend for a long session is likely undercounted, silently. Filed, not fixed - needs a transcript-structure diff, not more guessing.
- **Also found live**: production Postgres schema was never initialized (root cause of login looking broken for a long stretch — worked around, real fix pending), `server/Dockerfile` missing `scripts/` (account creation only worked via a live workaround, same status), a stale "(ZIP)" button label from an earlier feature removal, and `DEPLOYMENT.md` still describing both broken original steps — all fixed or documented as required workarounds the same day.
- Joakim: no browser `localStorage`, ever, for AI-session persistence (a misreading led to an unrelated, since-reverted POLICY.md edit about browser localStorage — corrected); push now happens automatically after every commit on this branch (was hand-over-only before).

## 2026-07-17 (4) — P0 deployment live

- **Deployed and reachable before the 14:00 deadline.** Full sequence: Docker installed on the home server from scratch (no `docker` apt package on Ubuntu 24.04 — used Docker's official `get.docker.com` convenience script instead); repo cloned; `.env` created with generated secrets; `docker compose -f docker-compose.prod.yml up -d --build` — all 5 containers came up clean, no crash loops.
- **Router work**: EdgeRouter X had SSH disabled by default (first attempt to configure port-forwarding over SSH silently failed — `ssh` connection was refused, and the pasted command block ran as no-ops in the local shell instead, which briefly produced a false "configured" doc entry, corrected same day). Enabled SSH via the web UI's System page, then configured port-forwarding via the EdgeOS CLI (`set port-forward rule 1/2 ...`, ports 80/443 -> 192.168.1.10), confirmed via `show port-forward`. **`hairpin-nat` is `disable`** on this router (noted in HARDWARE.md) — means devices on Joakim's own LAN can't reliably reach `photos.reuterborg.se` by its public DNS name (the request doesn't loop back in correctly), even though external access works fine. Caused a confusing false-alarm TLS warning when testing from Firefox on the LAN; real external testing (phone on mobile data) confirmed the deployment is actually correct.
- **DNS**: `photos.reuterborg.se` A record added at Inleed pointing to the public IP, root domain confirmed untouched throughout (`dig` before/after, done via a separate claude.ai session working the DNS/router side in parallel with this one).
- **Let's Encrypt**: Caddy obtained a real certificate for `photos.reuterborg.se` automatically once port-forwarding was live — no manual cert step. Confirmed via phone (mobile data, off the home LAN) that the site is reachable and the login gate correctly blocks unauthenticated access.
- **Caught and fixed mid-deploy**: `docker-compose.prod.yml` hardcoded the wrong photo path (`/home/joakim/Pictures/mammas_bilder`, copied from the dev compose file without verifying against the real server). Real path, confirmed by Joakim running `ls` on the server directly: `/tank/momfiles` (not even `/tank/mammas_bilder` as first guessed — corrected twice). Now sourced from a required `PHOTOS_HOST_PATH` env var instead of a literal in the tracked compose file. Verified after the fix: `docker compose exec photo-viewer ls /photos` shows the real album folders.
- **Account creation**: `create_account.py` command handed over for `elisabeth.reuterborg@gmail.com` (role member) — confirm directly with Joakim whether this was actually run and the phone login test passed; not independently verified by this session past handing over the command, since the deadline landed before that confirmation came back in chat.
- **Blast-radius discussion** (Joakim): raised whether an app-level compromise could reach the LAN/router. Answer documented in DEFERRED.md rather than just chat — confirmed no container runs privileged/host-networked (the main mitigation already in place), but flagged two real gaps as elevated-priority P1 items: photo-viewer's container running as root, and no egress restriction from the Docker network to the LAN.
- **New `documentation/bugs/` area** (Joakim's request, live during the post-deploy human checkpoint): a landing spot for bugs found in the moment, with a `TODO.md` untriaged list and a `reports/` subfolder for full multi-session investigation trails on the harder ones (first real one: the thumbnail-OOM bug below). `CLAUDE.md` now has a standing rule to check it periodically and at every session's end. Real bugs found and logged there today: `server/Dockerfile` never copies `scripts/` into the image (account creation only worked via a live workaround); the photo-viewer's static UI shell loads before any login check (confusing, not a security issue); thumbnails failing under concurrent load, likely OOM (unresolved — see the dedicated report).
- **Also added, from the same live checkpoint**: a hard resource-efficiency policy in `POLICY.md` (this must eventually run on Pi-class hardware, not just today's server — applies to every future code/dependency choice, not just performance-flagged work), and a Troubleshooting playbook in `DEPLOYMENT.md` capturing the diagnostic steps actually used to chase today's bugs, for reuse next time.
- Deferred, not built today: an always-present support/help button in the photo-viewer UI (Joakim's rough sketch: unobtrusive round blue button, white question mark) — needs its own design pass, logged in `documentation/bugs/TODO.md` conceptually but not yet a real ticket.

## 2026-07-17 (3)

- Documented the router (Ubiquiti EdgeRouter X, firmware 3.0.1, gateway 192.168.1.1) in HARDWARE.md, including the 80/443->192.168.1.10 port-forward set up for today's deploy. Gateway IP inferred from the dev workstation's `ip route` (same /24 subnet), flagged as such rather than presented as directly confirmed on the server. HARDWARE.md: 2424->3023.

## 2026-07-17 (2)

- **P0 under a hard 14:00 deadline**: gated the photo-viewer behind the auth backend's session cookie so Elisabeth can log in and see her pictures securely from the open internet, rather than Joakim driving ~40min to hand-deliver a zip. Added `app/auth.py` (stateless JWT verification, no Postgres dependency in this container by design) as a FastAPI dependency on every route that returns photo/thumbnail/voiceover data; `app.js` got a silent-refresh `authFetch` wrapper so the access token's short TTL doesn't interrupt browsing. Built `server/app/login_page.py` (TODO.md 1.10, previously unbuilt — API-only before today). Cut `ACCESS_TOKEN_EXPIRE_MINUTES` 15->5 (Joakim: prefers a smaller blind-trust window over relying on TTL alone; real revocation-recheck is a documented P1, see DEFERRED.md). Shipped a full production deployment: root-level `Caddyfile` + `docker-compose.prod.yml` (5 services: Caddy with automatic Let's Encrypt for `photos.reuterborg.se`, the photo-viewer, the auth+Postgres+Redis stack — one file because Caddy has to front two separately-built codebases) and `documentation/photo-server/DEPLOYMENT.md` as the execution handoff (UFW rules, `.env` setup, account creation, and a concrete restart-based persistence check for the analytics DB and voiceover recordings — not just a compose-file read). Knowingly overrode `HARDWARE.md`'s memtest gate for this one deploy (RAM upgrade ordered, not yet installed) — documented as a dated exception, not a removal of the gate. Discovered along the way: `mamma-photo-viewer` is an orphan branch with no shared git history with `master` (confirmed via `git merge-base` returning nothing), despite already containing byte-identical copies of `phase-1-login`'s auth backend files — so P0 ported wiring directly onto this branch rather than attempting a 24-conflict unrelated-histories merge under deadline pressure. Real merge preserving all three branches' history deferred to P1, no clock pressure — see TODO.md's new "Branch relationship" section. Deferred, documented, not silently dropped: access-token revocation recheck, multi-tenant photo partitioning (fine today since Elisabeth is the only account with photos), and whether `HARDWARE.md` belongs under a shared `documentation/hardware/` instead of `photo-server/` (see DEFERRED.md). Left the pre-existing stale dependency pins (fastapi/uvicorn/pillow/python-multipart) unbumped — Pillow's major version bump specifically carries real regression risk to working thumbnail code with no time to verify today. Doc size: DEFERRED.md 2349->4750, HARDWARE.md 1544->2424, README.md 5551->5369, TODO.md 30385->34620, DEPLOYMENT.md 0->4157 (new file). Tests: 49 (app/) + 47 (server/) = 96 passing, up from 49+45.

## 2026-07-17

- Removed the zip-download feature entirely — server endpoint, client JS, tests, and its docker volume — in favor of the sequential per-file transfer already used elsewhere. Confirmed by Joakim as a permanent decision (mum's real download over a slow/USB-drive link showed a single zip is all-or-nothing on failure), not a workaround. Split the voiceover feature's docs out of `documentation/gui/TODO.md` into their own `documentation/gui/voiceover/` subfolder. Fixed a stale test count left in `documentation/gui/README.md` (29 -> 24) from the zip-test removal. Commit `1945976`.
- Docker cleanup: the zip removal above left two dead zipcache volumes behind — this project's own (10.24GB, only detached once the container was recreated on the updated compose file) and a second copy on `mamma-photo-viewer_zipcache` (5.08GB), orphaned since the branch-mixup incident (see TODO.md's history note) left behind the old sibling-repo container's volumes with no container attached. Removed both, plus that same orphaned container's `_thumbcache`/ `_analytics_data` volumes and its unused image, 2 empty unattached anonymous volumes, and stopped this repo's own `photo_server_test_pg`/ `_redis` fixtures (forgotten running 19h past their test session, via their own `scripts/test_db.sh down` / `test_redis.sh down`). Local Docker volume usage: 15.56GB -> 129.8MB. `buzzkit-api`'s `api-worker-1` (a different project) was found still crash-looping under `unless-stopped` on missing config — left untouched, flagged to Joakim, not this repo's concern to fix.
- Project-level Claude Code permission settings (`.claude/settings.json`, tracked in git): added a blanket `Bash(*)` allow and `/var/lib/docker/volumes` to `additionalDirectories`, after a session where routine investigative commands kept hitting permission popups. Note for next session: destructive commands (`docker volume rm`, `docker rmi`, `docker run`) stay gated regardless — that floor isn't configurable from settings, by design.
- Tested whether the `Bash(*)` rule above actually suppresses popups: confirmed yes for ordinary and Docker read commands in this project (`ls`, `git log`, `docker ps`/`images`/`volume ls`/`system df` all ran without a prompt). Cross-repo Bash calls (`cd`-ing into a sibling project) still prompt — expected, matches the cross-repo caution rule in global CLAUDE.md, not a gap. One anomaly unresolved: a single `git -C <path> log ...` call prompted despite `Bash(*)`, while a plain equivalent in the same directory didn't; no hook or setting explains it — flag for a future session if it recurs.
- Traced Joakim's standing impression that "Docker must never be run directly, only handed over" to its actual source: not this repo, but `buzzkit/documentation/policies/POLICY.md`'s Docker/sudo rule, written when Docker needed `sudo` there. Verified this session the dev machine no longer needs `sudo` for Docker; relaxed that half of buzzkit's rule accordingly, left the VPS half gated (unverifiable — no direct VPS access), and added a follow-up note to `buzzkit/CLAUDE.md` to re-check the VPS side once its terminal output is next available. Edits made directly in buzzkit's working tree, uncommitted — cross-repo commits need asking first, per global CLAUDE.md.
- Confirmed `docker run` (via `server/scripts/test_db.sh`/`test_redis.sh`) keeps prompting even with `Bash(*)` already in effect — proof, not just the earlier note's suspicion, that this class of command (`docker run`/`rmi`/`volume rm`) is gated above the settings.json allow-list layer, not by it. Since `Bash(*)` is already the broadest possible pattern, no narrower docker-specific rule could ever suppress it either — there's no rule to add or remove here, the floor isn't reachable from settings at all.
- While drafting a next-session starting prompt for GUI login + branch merges: fixed stale doc drift in `documentation/photo-server/README.md`'s "Priority order" section — it still posed "does Phase 1 adapt Joakim's buzzkit login implementation or build fresh" as an open question, contradicting the same file's own Status section a few lines up, which already said that was decided and executed (ported from buzzkit, argon2id, JWT+redis, steps 1.1–1.8 done). Confirmed via buzzkit's own CHANGELOG (Rev 4/5, 2026-07-05) that its login/auth — signup, lockout, Google OAuth, JWT refresh/logout, RLS isolation, GDPR erasure — was finished and tested long before today; the stale line was simply never updated once the decision was made. Not an open question anymore.

---

**Below this point: this repo's original mainline history (`master`), continuous through 2026-07-16 — the point `mamma-photo-viewer` diverged from as an orphan branch. Its own changelog continues above.**

## 2026-07-16 (32)

- Added a durable roadmap principle to TODO.md, prompted by Joakim:
  "every major todo should end with a human test revealing user-made
  bugs (if the user can do wrong, the user WILL do wrong)" — misuse
  testing, not just the happy path, and this requires that phase's GUI
  to actually be finished by then (not just its API), since layout bugs
  like overflowing text boxes only show up on a real rendered screen.
  Audited every phase: Phase 4 had no human checkpoint at all (added
  one, misuse-focused, plus a note that it also covers 4.8/4.9 once
  those specs exist); Phase 1's 1.11 and Phase 5's existing checkpoint
  were happy-path only (both got misuse-testing additions — empty/
  whitespace fields, absurd input length, double-submit, browser
  back/forward, narrow-window overflow, rapid repeated taps); Phase 2
  got an explicit "no checkpoint, by design" note instead of silence,
  since it has no user-facing behavior to test. Also updated the
  photo-server README.md status line to reflect 1.1–1.8 done (40 tests
  green) and the roadmap gaps found and fixed this session. No code —
  documentation only. Doc character counts:
  `documentation/photo-server/TODO.md` 24767 → 27444 (+2677),
  `documentation/photo-server/README.md` 4807 → 5402 (+595).

## 2026-07-16 (31)

- Closed a real roadmap gap in TODO.md, found by Joakim asking where
  the GUI gets built: every Phase 1 step through 1.9 built the login
  API only — nothing built an actual page a person could open in a
  browser, unlike Phase 4.6 which explicitly builds the thumbnail
  screen's frontend. Added new 1.10 (login page frontend per
  MOCKUP.md, wired to `POST /login`) before the human checkpoint,
  renumbered to 1.11. Audited every later phase for the same gap per
  Joakim's follow-up ask ("add steps on every major update where gui is
  applicable") and found two more: added 4.8 (lightbox + info panel)
  and 4.9 (search/filter panel, wired to 4.3). Both of those, unlike
  1.10, failed a second check Joakim then asked for explicitly — a
  concrete definition of "well-defined GUI spec," using MOCKUP.md's
  Login screen section as the bar (every field/element present and
  explicitly what's absent, every state with exact user-facing wording,
  the transition for each state, which backend endpoint(s) it calls,
  what's deferred and to where). MOCKUP.md only *names* "lightbox, info
  panel, search/filter panel" with none of that detail, so 4.8/4.9 are
  marked **(blocked on spec)** rather than presented as build-ready —
  the actual UX decisions (lightbox navigation, info panel layout,
  search panel fields) are Joakim's to make, not something to invent to
  fill the gap. Both new practices ("pair every user-facing phase with
  a frontend step" and "GUI steps need a spec at this bar before
  they're buildable") added to TODO.md's "How to use this roadmap"
  section so they apply going forward, not just as one-off fixes. No
  code yet — this commit is the roadmap fix only. Doc character count:
  `documentation/photo-server/TODO.md` 21625 → 24767 (+3142).

## 2026-07-16 (30)

- photo-server TODO.md 1.8 (rate limiting): new `app/rate_limit.py`
  (`slowapi`'s `Limiter`, Redis-backed, IP-keyed), registered in
  `app/main.py`, `"5/minute"` on `POST /login`. TDD: `tests/
  test_rate_limit.py` written failing first (6 requests, asserted the
  6th returns 429 — failed at first since the limiter didn't exist yet).
  Caught a test-isolation gap while wiring it in: the limiter's Redis
  state persists across the whole test run and keys on client IP, which
  `TestClient` always reports as one fixed address, so an earlier test's
  login attempts were bleeding into a later test's limit once both
  existed. Fixed by making the shared `client` fixture always flush
  Redis before/after (via the existing `redis_client` fixture), not only
  for tests that request it directly. Also fixed a duplicated paragraph
  in this file left over from an earlier edit (1.8's text had been
  pasted twice). Full suite: 40/40 green (was 39/39 before this step),
  confirmed stable across two consecutive runs. Doc character count:
  `documentation/photo-server/TODO.md` 21465 → 21625 (+160).

## 2026-07-16 (29)

- Tightened `CLAUDE.md`'s TDD bullet: dropped "where practical", now
  strict with no exceptions. Prompted by Joakim after a real slip this
  session (a small helper written before its test) and a follow-up
  question about whether that lesson was only going in private AI
  memory — it was, initially; per this repo's own self-sufficiency
  rule, the actual rule now lives here instead of only there. Doc
  character count: `CLAUDE.md` 8819 → 9482 (+663).

## 2026-07-16 (28)

- photo-server TODO.md 1.7 (audit log on login): `audit_log` table
  pulled forward into `app/db.py`'s `ensure_schema`; new
  `app/audit.py`'s `log_audit_event`, wired into `app/auth_routes.py`'s
  login handler for both `login_failure` (with the attempted email in
  `details`) and `login_success`. One process note: the standalone
  `log_audit_event` unit test (`tests/test_audit.py`) was written after
  its implementation, not before — a slip, caught and disclosed in
  conversation rather than backfilled quietly; TDD stayed strict for
  everything since. **Real bug found and fixed while wiring the audit
  calls into the login route**: `app/db.py`'s `get_db()` only
  auto-committed after a route returned cleanly; a raised
  `HTTPException` (the failed-login path) is thrown into the dependency
  generator at its `yield` point, skipping that commit entirely, so the
  failed-login audit row this step exists to produce would have been
  silently dropped in the real deployed app. Not caught by the test
  suite itself, since the test override shares the test's own
  already-open transaction (no commit needed to see its own writes) —
  found via code review, not a failing test. Fixed by dropping the
  auto-commit and committing explicitly at each route's actual write
  points (matching `scripts/create_account.py`'s existing convention);
  the test `client` fixture now also no-ops `db_connection.commit()` via
  `monkeypatch` so a route's real commit call doesn't finalize seeded
  test rows into the disposable database (which would otherwise break
  repeated local test runs against the same long-lived container with
  duplicate-email violations). TDD: `tests/test_auth_routes.py` gained
  3 new tests, written failing first. Full suite: 39/39 green (was
  35/35 before this step), verified stable across two consecutive runs
  against the same test container. Doc character count:
  `documentation/photo-server/TODO.md` 20122 → 21465 (+1343).

## 2026-07-16 (27)

- photo-server TODO.md 1.3–1.6 (login route, generic error, protected
  route, token expiry): new `app/auth_routes.py` (`POST /login`,
  `GET /whoami`, `get_current_user` dependency) and `app/cookies.py`
  (`set_auth_cookies`/`clear_auth_cookies`), ported from buzzkit and
  adapted to raw psycopg. **Real bug found and fixed, not just
  ported-and-trusted**: buzzkit's own login route short-circuits
  (`auth_row is None or not verify_password(...)`), so an unknown email
  skips the expensive argon2 verify and returns measurably faster than a
  wrong-password attempt — a timing side channel that discloses which
  emails are registered. Fixed here by always calling `verify_password`
  (against a precomputed dummy hash when no user exists) regardless of
  whether the email exists, with a test asserting the call count is
  identical either way. Also added `app/db.py`'s `get_db()` FastAPI
  dependency (wraps `get_connection()`) so tests can override it to
  share the test's own transaction — avoids a second, separately-committed
  connection that would've left permanent rows in the disposable test
  database across repeated local runs. 1.6 (token TTLs) was already
  covered by the prior token-layer commit's tests, marked done here.
  TDD: new `tests/test_auth_routes.py` (7 tests) written failing first.
  Full suite: 35/35 green (was 28/28 before this step). Doc character
  count: `documentation/photo-server/TODO.md` 19239 → 20122 (+883).

## 2026-07-16 (26)

- photo-server Phase 1 prerequisite (feeds 1.3–1.6): JWT access/refresh
  token layer. `app/config.py` gained `load_auth_config()` (same
  fail-fast, no-defaults pattern as 0.4's `load_db_config`, now for
  `REDIS_URL`/`JWT_SECRET_KEY`), wired into `app/main.py`'s import-time
  check alongside the DB config. New `app/tokens.py` — access tokens
  (15 min TTL) and refresh tokens (12h TTL, Redis-allowlisted so
  logout/rotation can revoke one early), ported from buzzkit's
  `app/core/security.py`, with the redis client passed in explicitly
  rather than module-global for testability. TDD: `tests/test_tokens.py`
  (7 tests — round trips, wrong-type rejection for both token kinds,
  expiry for both via a backdated `now` parameter rather than a real
  sleep or a mocked clock library, and revocation) written failing
  first. New `server/scripts/test_redis.sh` (disposable test Redis,
  mirrors `test_db.sh`) plus a `redis_client` pytest fixture in
  `conftest.py`. Full suite: 28/28 green (was 18/18 before this step).
  Doc character count: `documentation/photo-server/TOOLCHAIN.md` 2104 →
  2796 (+692).

## 2026-07-16 (25)

- photo-server TODO.md 1.2 (account-creation CLI): new
  `server/app/accounts.py`'s `create_account` (raw SQL insert using
  1.1's `hash_password`) plus `server/scripts/create_account.py`, a
  thin argparse wrapper reading the password from
  `CREATE_ACCOUNT_PASSWORD` or a non-echoed prompt — never a CLI
  argument, to avoid leaking it into shell history/process listings.
  TDD: `tests/test_accounts.py` (row insert + duplicate-email rejection)
  written failing first. Also hand-ran the actual CLI against the
  disposable test container per this project's verify discipline, which
  caught a real bug the unit tests couldn't: invoking the script
  directly doesn't put `server/` on `sys.path`, so `app` wasn't
  importable — fixed by adding `scripts/__init__.py` and switching the
  documented invocation to `uv run python -m scripts.create_account`.
  Full suite: 18/18 green (was 16/16 before this step). Doc character
  count: `documentation/photo-server/TODO.md` 18614 → 19239 (+625).

## 2026-07-16 (24)

- photo-server README.md status line updated: Phase 0 done, Phase 1 in
  progress on `phase-1-login` with 1.1 done, next up is 1.2. Doc
  character count: `documentation/photo-server/README.md` 4700 → 4807
  (+107).

## 2026-07-16 (23)

- photo-server TODO.md 1.1 (password hashing helper): new
  `server/app/security.py`'s `hash_password`/`verify_password`/
  `needs_rehash`, ported from buzzkit's `app/core/security.py` using
  `argon2-cffi`'s `PasswordHasher` (argon2id). TDD: new
  `tests/test_security.py` (5 tests — round trip, wrong-password
  rejection, an explicit assertion the produced hash is actually
  `$argon2id$` rather than assumed, and both branches of
  `needs_rehash`) written failing first, then made to pass. Full suite:
  16/16 green (was 11/11 before this step). Doc character count:
  `documentation/photo-server/TODO.md` 18540 → 18614 (+74).

## 2026-07-16 (22)

- Phase 1 (login) architecture decided, on new branch `phase-1-login`:
  reuse Joakim's existing login implementation from the sibling
  `buzzkit` repo (`../../project/buzzkit`) instead of building this
  phase's original bcrypt/DB-session fallback spec from scratch, per
  Joakim's explicit ask to shorten build time. Two deviations from
  buzzkit's code confirmed with Joakim rather than assumed: argon2id
  (not bcrypt) for password hashing — OWASP's current recommendation —
  and JWT access+refresh tokens with Redis-backed revocation (not a
  plain Postgres session table) for sessions, trading a new `redis`
  service for buzzkit's own tested code. Refresh-token TTL set to 12h
  (not buzzkit's 30 days) to preserve this spec's original session-length
  intent for a small private server. Not ported: `/signup`, Google OAuth
  (violates this project's no-cloud-APIs rule), analytics/activity
  emission, buzzkit's username-keyed account lockout (superseded by
  `slowapi`'s IP-keyed rate limiter, which already satisfies this
  phase's 1.8 on its own), and buzzkit's separate least-privilege
  `security_writer` DB role (deferred, not proportionate at two-user
  scale yet). This commit is scaffolding only, no auth code yet: added
  `argon2-cffi`/`pyjwt`/`redis`/`slowapi` to `server/pyproject.toml`
  (`>=`-only, resolved to latest via `uv lock`, `pip-audit`-clean);
  added a `redis` service to `server/docker-compose.yml` (128m-capped,
  internal-only, `requirepass` via env var, `restart: "no"` — buzzkit's
  own compose file uses `unless-stopped` here, deliberately not carried
  over); added `REDIS_PASSWORD`/`JWT_SECRET_KEY` to `.env.example`;
  rewrote TODO.md's Phase 1 section end-to-end for the new architecture;
  updated DATA_DICTIONARY.md's `password_hash` column note. Full suite
  still 11/11 green (no app code touched). Doc character counts:
  `documentation/photo-server/TODO.md` 14166 → 18540 (+4374),
  `documentation/photo-server/DATA_DICTIONARY.md` 4687 → 4764 (+77).

## 2026-07-16 (21)

- Dependency/CVE check across `server/`, prompted by Joakim asking for a
  version update after CVE warnings on other repos — also the first
  application of entry (20)'s new policy, applied retroactively to 0.4.
  `uv lock --upgrade` produced no diff: every dependency (`fastapi`
  0.139.0, `psycopg` 3.3.4, `uvicorn` 0.51.0, `httpx2`/`httpcore2` 2.7.0,
  `pytest` 9.1.1, and transitive deps) was already resolved to its
  newest version, since `pyproject.toml`'s `>=`-only constraints let `uv
  sync` pick latest by default. `pip-audit` (run via `uvx --python 3.13`
  — the system's `/usr/bin/python3.12` lacks a working `ensurepip`, so
  `uvx` needs a uv-downloaded interpreter instead, same gap
  [TOOLCHAIN.md](documentation/photo-server/TOOLCHAIN.md) already notes
  for `uv sync`) found no known vulnerabilities in either the production
  or full (prod+dev) dependency set. Also checked the two pinned Docker
  base images: `postgres:18.4-bookworm` is Docker Hub's current tag and
  is itself the release that fixed 11 CVEs (not one needing a further
  patch); `python:3.12-slim-bookworm` is a floating tag, always latest
  on rebuild. No changes needed. Full suite re-run: 11/11 green.

## 2026-07-16 (20)

- New non-negotiable in `CLAUDE.md`: check for newest dependency
  versions before every numbered TODO step (not just once per phase, and
  not only when a CVE prompts it); if updating surfaces an incompatible
  or breaking newer version, fixing that break is the priority — no
  quiet revert-and-move-on. Joakim's call, made concrete because 0.4 (the
  previous commit) was implemented against already-pinned versions
  without a fresh check first. Granularity (per-step, not per-phase) and
  location (`CLAUDE.md` globally, not scoped to one topic's TODO.md)
  both confirmed with Joakim rather than assumed. Doc character count:
  `CLAUDE.md` 8280 → 8819 (+539).

## 2026-07-16 (19)

- photo-server TODO.md 0.4 (env-var-only DB config, fail-fast on a
  missing var): new `server/app/config.py`'s `load_db_config()` reads
  the five `POSTGRES_*` vars with no fallback defaults and raises
  `MissingConfigError` if any are missing; `app/main.py` calls it at
  module import time so the app refuses to start before binding a port
  rather than failing lazily on the first DB-touching request.
  `app/db.py`'s `get_connection()` now goes through the same loader
  instead of repeating `os.environ[...]` inline. TDD: new
  `tests/test_config.py` (6 tests: happy path, one per missing var,
  plus an import-time-reload check on `app.main`) written failing
  first, then made to pass. Also fixed a real gap this step's tests
  exposed: `docker-compose.yml`'s `app` service defined no `POSTGRES_*`
  environment at all — with the new fail-fast check in place that would
  have kept the real container from starting — now wired through
  against the `postgres` service. Full suite: 11/11 green (was 4/4
  before this step). Doc character counts:
  `documentation/photo-server/TODO.md` 13595 → 14166 (+571),
  `documentation/photo-server/README.md` 4477 → 4700 (+223).

## 2026-07-16 (18)

- Session wrap-up audit: git clean, 33/33 tests green (29 tool + 4
  server), no dangling Docker images/containers, all 24 tracked `.md`
  files' cross-references resolve, lockfile matches manifest, no stale
  FIXME/TODO drift from this session's changes. Two real gaps found and
  fixed separately: the "auto" permission-mode recommendation was never
  actually applied (flagged back to Joakim — needs his `/config` action,
  not something I can do); and this session went the entire way without
  writing anything to the auto-memory store despite substantial feedback
  — fixed by adding two feedback memories (exact-measurements-over-
  estimates; permission-pushback-and-written-policy).
- **Forward-effectiveness note**: this session's `commit_cost` bugs
  (`<synthetic>`-model pricing block, the `tools/*/metrics.py` bare-import
  collision) were only caught because both tool test suites happened to
  get run *together* once. There's no single "run everything" command in
  this repo today — `tools/doc_metrics` + `tools/commit_cost`'s unittest
  suites and the server's pytest suite (behind `test_db.sh up`/`down`)
  are three separate manual invocations. Worth considering a single
  wrapper script next time test infrastructure is touched, so a future
  cross-suite bug doesn't depend on remembering to combine them by hand.
  Not built now — noted as a suggestion, not a decision.

## 2026-07-16 (17)

- Redundancy + doc-location audit, prompted by Joakim asking "is that not
  a rule?" about documentation living under `documentation/`. Checked the
  actual written rule (`CLAUDE.md`'s Documentation layout section) and
  found it only governs `documentation/`'s own internal structure plus
  two explicit exceptions (root `README.md`, `CLAUDE.md`) — it never
  addressed `server/README.md` or the two `tools/*/README.md`s, which had
  drifted into holding real content outside `documentation/`. Per
  Joakim's decision: moved that content in — `server/README.md`'s
  toolchain notes → `documentation/photo-server/TOOLCHAIN.md`;
  `tools/doc_metrics/README.md` and `tools/commit_cost/README.md` → new
  `documentation/tooling/` (project-wide utilities, not tied to one
  topic) — and left one-line stub `README.md`s in the code directories
  for IDE discoverability. Made this an explicit written rule in
  `CLAUDE.md` so it doesn't drift again. Also fixed the one real
  redundancy the audit found: `CLAUDE.md`'s privacy bullet restated
  `POLICY.md`'s EXIF/GPS and distributed-sync specifics instead of
  cross-referencing them, against `POLICY.md`'s own "nothing project-wide
  duplicated outside this file" rule — trimmed to a cross-reference.
  Updated every affected link (six code docstrings, two README index
  tables) and verified all of them resolve. Doc character counts:
  `CLAUDE.md` 7633 → 8280 (+647), `documentation/README.md` 634 → 729
  (+95), `documentation/photo-server/README.md` 4388 → 4477 (+89),
  `server/README.md` 2004 → 241 (-1763, now a stub),
  `tools/doc_metrics/README.md` 6298 → 219 (-6079, now a stub),
  `tools/commit_cost/README.md` 5136 → 219 (-4917, now a stub); new:
  `documentation/photo-server/TOOLCHAIN.md` 2104,
  `documentation/tooling/README.md` 656,
  `documentation/tooling/DOC_METRICS.md` 6712,
  `documentation/tooling/COMMIT_COST.md` 5378.

## 2026-07-16 (16)

- `commit_cost` was documented in its own README but nowhere else —
  found while Joakim asked "is the new metrics and the old metrics
  documented?" Fixed two real gaps: (1) `CLAUDE.md` mandated running
  `doc_metrics`'s `log.py` after every commit but never mentioned
  `commit_cost` at all, so a fresh session with zero prior context
  wouldn't know to keep doing it — added a standing rule mirroring the
  `doc_metrics` one, per Joakim's explicit call to make it a written
  requirement, not just a habit this session picked up; (2) the two
  tools' READMEs only cross-linked one way (`commit_cost` → `doc_metrics`)
  — added the reverse link. Doc character counts: `CLAUDE.md` 7181 → 7633
  (+452), `tools/doc_metrics/README.md` 6103 → 6298 (+195).

## 2026-07-16 (15)

- Added `tools/commit_cost`: exact per-commit token/dollar cost, distinct
  from `doc_metrics` (which measures document *size*, not the cost of
  producing it). Reads Claude Code's own session transcripts
  (`~/.claude/projects/<slug>/*.jsonl`) — every assistant turn's
  `message.usage` carries the actual billed tokens, not an estimate — and
  anchors on each `git commit` tool call's real result hash to sum usage
  exactly between one commit and the next. Per Joakim's explicit
  correction: a human-authored commit (no matching session) logs a real
  `0`, never a null "unknown" — that's what makes human-vs-LLM cost
  comparisons meaningful. `cost_usd` is null only when tokens are known
  but genuinely unpriceable (mixed/unrecognized model in one commit).
  `session_id` captured per commit too (`sessionId` is already on every
  transcript row) for a `report.py --by-session` view. Caught and fixed
  one real bug before trusting it: Claude Code's `<synthetic>`
  (zero-usage, compaction-related) rows were polluting the per-commit
  `models` list and wrongly blocking pricing — regression-tested.
  Verified end-to-end against this repo's real history: 45 LLM-assisted
  commits, 72 human-only, ~$97.72 total. Also fixed a latent bug this
  surfaced: `doc_metrics/test_metrics.py` and `commit_cost/test_metrics.py`
  both did a `sys.path` + bare `import metrics`, which collide in
  `sys.modules` when both suites load in one process — switched to
  qualified imports (`from tools.<name> import metrics`). Doc character
  counts: `tools/commit_cost/README.md` (new) 5136.

## 2026-07-16 (14)

- Clarified `tools/doc_metrics/README.md`'s opening: it only stated the
  mechanical goal (measure char growth consistently) not the actual
  reason Joakim wants it (a cost ledger tied to outcomes/tasks). Fixed
  the framing regardless of the bigger `commit_cost` discussion that
  followed in the same session. Doc character counts:
  `tools/doc_metrics/README.md` 5789 → 6103 (+314).

## 2026-07-16 (13)

- Renamed `metrics.jsonl`'s keys to match `metrics.db`'s column names
  exactly (`ts`→`recorded_at`, `commit`→`commit_hash`, `file`→
  `file_path`, `chars`→`char_count`), per Joakim's readability ask.
  Applied to all 736 existing rows — a pure key-rename, values
  untouched, so kept despite the append-only design (renaming a key's
  spelling isn't rewriting a past entry's meaning). Also clarified for
  Joakim that `metrics.db` was already gitignored (never committed), so
  the jsonl+db split isn't paying a double storage cost in git — only
  `metrics.jsonl` is. Doc character counts:
  `tools/doc_metrics/README.md` 5219 → 5789 (+570).

## 2026-07-16 (12)

- Fixed a real bug in `tools/doc_metrics` found while confirming its
  char/token tracking to Joakim: `discover_md_files` was a raw filesystem
  walk (`root.rglob("*.md")`), so every regular post-commit `log.py` run
  (not `--backfill`, which already used `git ls-tree` correctly) picked
  up vendored `*.md` files inside gitignored `server/.venv/` — license
  files, a bundled FastAPI skill doc. ~21.6% of all summed characters
  logged to date (427,518 of 1,974,536) was this pollution, and it broke
  the tool's own "every snapshot scoped identically" goal since `.venv`
  contents vary per machine/install. Fixed by scoping to `git ls-files`
  instead; historical `metrics.jsonl` rows left as-is (append-only, same
  precedent as the earlier codepoint-vs-`wc -c` switch), documented in
  `tools/doc_metrics/README.md`. Also added `--task` to `log.py` (labels
  a snapshot with the TODO item/outcome it served) and `--by-task` to
  `report.py` (cost grouped by task) — Joakim wants doc growth traceable
  to what it paid for, not just tracked in the aggregate. `uv run
  pytest`/`unittest` both green (14/14); `metrics.db` rebuilt from the
  git-tracked jsonl to pick up the new `task` column. Doc character
  counts: `tools/doc_metrics/README.md` 3662 → 5219 (+1557).

## 2026-07-16 (11)

- Implemented photo-server TODO.md step 0.3: `users` table (id, email,
  password_hash, role, created_at), psycopg3 + raw SQL per Joakim's
  choice over SQLAlchemy/asyncpg (`app/db.py`), TDD round-trip +
  `unique(email)` tests. Also added `scripts/test_db.sh`, a disposable
  Postgres container for local test runs — the committed
  `docker-compose.yml` deliberately never publishes Postgres's port to
  the host, so plain `pytest` had nothing to connect to; documented in
  `server/README.md`'s new "Testing against Postgres" section. Doc
  character counts: `documentation/photo-server/README.md` 4186 → 4388
  (+202), `server/README.md` 1189 → 2004 (+815).

## 2026-07-16 (10)

- Three more global rules added (`~/.claude/CLAUDE.md`), from Joakim
  asking directly what would make communication more effective: doc-drift
  audits become standing practice at every session close (not just
  when asked — this session's three real drifts only got found because
  they were explicitly requested); no placeholder tool calls (a couple
  slipped through this session); denser bookkeeping updates for repeated
  no-news cycles (test → commit → log-metrics → commit ran ~10+ times
  today, each narrated individually).

## 2026-07-16 (9)

- New global rule (`~/.claude/CLAUDE.md`): keep a current-status line in
  each project's entry doc, updated whenever a phase/step completes.
  Prompted by this session's own experience — asked to estimate a fresh
  session's catch-up cost, the answer came out to ~500-800 characters
  specifically because `documentation/photo-server/README.md`'s status
  line had just been fixed from stale ("planning only, no code written
  yet") to current. Generalizing that habit the same way the CHANGELOG
  discipline was generalized earlier today.

## 2026-07-16 (8)

- Session-wrap-up audit: compared TODO.md's Phase 0 wording against what
  was actually built. Found three drifts, all fixed: 0.1 said "pytest +
  httpx" but the actual dev dependency is `httpx2` (Starlette deprecated
  plain `httpx` in `TestClient` — see the 0.1 commit) — reworded to
  "pytest + FastAPI's `TestClient`" instead of naming a library
  underneath it, so this doesn't re-drift if that changes again; 0.2 said
  "curl /health from inside a container" but the actual (and correct)
  checkpoint curled the published port from the host — reworded to match;
  `server/pyproject.toml` still had uv's placeholder description
  ("Add your description here"), never filled in. Char counts
  (codepoints): `TODO.md` 13488 → 13595 (+107).

## 2026-07-16 (7)

- Checked the no-auto-restart Docker rule from entry (6) against Docker's
  own docs rather than assume it was "best practice" — it isn't one
  Docker prescribes at all (their only stated guidance is "use restart
  policies, avoid process managers"); it's a deliberate, stricter-than-
  typical choice for this project's specific threat (silent re-exposure
  on an untrusted network), not an industry default. Refined the global
  rule (`~/.claude/CLAUDE.md`) to the actual right shape: dev base file
  stays `restart: "no"`, production restores `unless-stopped` via a
  separate Compose override file (`compose.prod.yaml`-style) invoked
  only explicitly at deploy time — Compose auto-loads
  `compose.override.yaml` and nothing else, so this can't activate by
  accident. Added a pointer for this at TODO.md's new step 6.0, so
  Phase 6 doesn't forget it. Char counts (codepoints): `TODO.md`
  13154 → 13488 (+334).

## 2026-07-16 (6)

- Cross-project finding: `buzzkit-api`'s `worker` container had been
  crash-looping (~24h) on missing `JWT_SECRET_KEY`/`COOKIE_DOMAIN` env
  vars. Documented (not fixed, not committed — a different repo, and
  Joakim declined the in-session commit) in that project's own
  `api/README.md`/`CHANGELOG.md`. Logging it here too, since the
  cross-repo rules below only exist in `~/.claude/CLAUDE.md`, which
  isn't tracked in any repo — this entry is the searchable, per-project
  record of what changed and why.
- New global rules added to `~/.claude/CLAUDE.md` (this session, prompted
  by the buzzkit finding above): (1) no dev/test Docker service gets an
  auto-restart policy (`restart: "no"`/omitted, not `unless-stopped`/
  `always`) by default — a container that silently comes back after a
  daemon restart or reboot is a real exposure risk (e.g. reconnecting on
  open wifi without knowing something's listening); (2) committing to a
  repo other than the one a session is rooted in always needs asking
  first, every time, even though committing *within* the active project
  stays standing-authorized; (3) cross-project findings go into the
  target project's existing docs structure (README/TODO/CHANGELOG), not
  a new dedicated inbox file — decided over standardizing one, since
  most projects already have a place this fits.
- Fixed `server/docker-compose.yml` to comply with rule (1) above:
  both `app` and `postgres` were `restart: unless-stopped`, now
  `restart: "no"`.

## 2026-07-16 (5)

- Closed two documentation gaps found on an explicit audit pass ("what's
  undocumented"): added `server/README.md` explaining why `server/` uses
  uv instead of pip/venv (this dev machine's `ensurepip`/`python3-venv`
  is broken — previously only mentioned in passing in TODO.md), and
  generalized the README.md↔HARDWARE.md circular-reference bug fixed
  earlier this session into a durable rule in CLAUDE.md's lean/exact
  bullet ("cross-references must terminate"). Char counts (codepoints):
  `CLAUDE.md` 6829 → 7181 (+352), `server/README.md` 0 → 1189 (new).

## 2026-07-16 (4)

- Merged `photo-server-planning` into `master` (fast-forward, no
  conflicts) per Joakim's specified procedure: pull the feature branch,
  pull master, merge master into the feature branch first, only then
  fast-forward master onto it. Fixed a stale status line in
  `documentation/photo-server/README.md` — it still said "planning only,
  no code written yet" after 0.1 and 0.2 were both built and
  checkpointed this session. Char counts (codepoints): `README.md`
  4031 → 4186 (+155).

## 2026-07-16 (3)

- Step 0.2 human checkpoint passed: Joakim ran `docker compose up --build`
  (after stopping an unrelated stray container, `buzzkit-api`'s
  `api-api-1`, that had squatted on port 8000 for 23h) and confirmed
  `curl /health` returns 200 `{"status":"ok"}` with no `Server` header.
  Postgres 18.4 initialized cleanly at `/var/lib/postgresql/18/docker`,
  confirming the volume-path fix. Phase 0 scaffold (0.1 + 0.2) is done.

## 2026-07-16 (2)

- Added a "Branching and merging" rule to CLAUDE.md at Joakim's request:
  ask and suggest a new branch before starting non-trivial new dev work,
  and never merge into main without confirmation each time. Merging
  differs from push/force-push/history-rewrite (always handed over as a
  copyable command) — once Joakim confirms a merge, the AI session runs
  it directly rather than handing it back. Scoped to this repo, not the
  new global `~/.claude/CLAUDE.md`, per Joakim's answer. Char counts
  (codepoints): `CLAUDE.md` 6178 → 6829 (+651).

## 2026-07-16

- Fixed `server/docker-compose.yml`'s postgres volume mount: it targeted
  `/var/lib/postgresql/data`, the pre-18 convention, which postgres:18+
  refuses to start against (`pg_ctlcluster`-style versioned layout now
  expected). Root cause was a research gap I should have caught before
  writing the file, not a new discovery — 0.2's own commit already cited
  a web search noting "PostgreSQL 18 using /var/lib/postgresql/18/docker"
  but that fact never got applied to the actual mount path. Confirmed
  the fix (mount at `/var/lib/postgresql`, not `.../data`) against
  docker-library/docs's postgres content.md before changing it, rather
  than guessing a second time. Found via Joakim running the step 0.2
  checkpoint himself and hitting the failure.

## 2026-07-15 (13)

- Wrote and built (not run) photo-server TODO.md step 0.2: `server/Dockerfile`
  (multi-stage uv build per Astral's documented pattern, non-root
  `appuser`, `uvicorn --no-server-header` closing 0.1's tracked header
  leak — confirmed the flag exists via `uvicorn --help` before using it),
  `server/docker-compose.yml` (`app` published to 127.0.0.1 only,
  `postgres:18.4-bookworm` with no published port, both with explicit
  `mem_limit`, `POSTGRES_PASSWORD` required via `.env` with no
  hardcoded/blank fallback), `.dockerignore`, `.env.example`. Verified
  postgres 18.4 is current stable via web search rather than assuming a
  version. Image builds clean (201MB, confirmed non-root user and CMD by
  inspecting the built image). `docker compose up` and the curl smoke
  test are still Joakim's to run — both the standing human-checkpoint
  rule and HARDWARE.md's unconfirmed-RAM-upgrade gate apply. Confirmed
  with Joakim that the machine this session runs on is a separate dev
  box from the actual target host (192.168.1.10) — see HARDWARE.md.

## 2026-07-15 (12)

- Fixed two photo-server doc gaps found while explaining the deployment
  environment to Joakim: README.md and HARDWARE.md pointed at each other
  for the "why Docker Compose, not native install" reasoning without
  either stating it — a circular reference, not an actual cross-link.
  HARDWARE.md is now the canonical owner of that reasoning (shared ZFS
  pool → dependency/root-access collision risk), README.md points to it
  one-way. Separately, TODO.md step 0.2's human checkpoint didn't
  reference HARDWARE.md's "don't run `compose up` until the RAM upgrade
  is memtested" gate — a session reading only TODO.md (the file its own
  README tells you to start with) could miss it; added an explicit
  pointer. Char counts (codepoints): `README.md` 4016 → 4031 (+15),
  `HARDWARE.md` 936 → 1129 (+193), `TODO.md` 12977 → 13154 (+177).

## 2026-07-15 (11)

- Implemented photo-server TODO.md step 0.1 (`GET /health`) via TDD:
  failing pytest first, then the minimal FastAPI route. System had no
  `pip`/working `venv` (`ensurepip` missing, no `python3-venv` package) —
  a system-level install per POLICY.md, so handed the fix to Joakim as a
  copyable `apt install` command; he redirected to `uv` instead, which
  needs no system package and resolved everything into `server/.venv`.
  New `server/` is a self-contained uv project (`fastapi`, `uvicorn`,
  `pytest`, `httpx2` — not plain `httpx`, since Starlette's `TestClient`
  now deprecates it in favor of `httpx2`, confirmed by reading
  `starlette/testclient.py` rather than assuming). Manually ran the app
  and curled it for real (TestClient can't see this, since it bypasses
  the transport layer) and found uvicorn's default `Server: uvicorn`
  header leaks the stack, failing 0.1's own Security line; rather than
  fix it in-place (scope belongs to whichever step defines the real run
  command), added a tracked note to TODO.md step 0.2 to launch with
  `server_header=False`. Char counts (codepoints): `TODO.md` 12629 →
  12977 (+348).

## 2026-07-15 (10)

- Trimmed two cross-file/within-file duplications found while auditing
  `documentation/` for excess length at Joakim's request: `VISION.md`
  Pillar 3 fully restated the closed-vs-opt-in trust-boundary tension
  already owned by `POLICY.md`'s Open questions section (POLICY.md's own
  rule: nothing project-wide duplicates outside it) — now a one-line
  pointer. `photo-server/README.md` repeated its own Non-negotiables
  Postgres/pgvector reasoning in its closing paragraph — now stated
  once. No information removed, only the second copy of each fact.
  Char counts (codepoints): `VISION.md` 3718 → 3483 (−235),
  `photo-server/README.md` 4057 → 4016 (−41); −276 net.

## 2026-07-15 (9)

- Fixed a scope mismatch Joakim spotted by auditing every root
  `documentation/` folder against its own stated purpose:
  `photo-server/DPFAS_VISION.md` opened with "the standing goal across
  the whole project," directly contradicting its own folder's README
  ("one narrow, closed slice... nothing here should grow toward...
  AI-driven curation suggestions"), and its three-UX-path table
  duplicated `DATA_DICTIONARY.md`'s Tag-dimensions table in the same
  folder. Deleted the file (per Joakim's choice among three options
  offered); its only non-duplicated content — the Postgres/pgvector
  rationale — moved into `photo-server/README.md`'s existing
  "Relationship to the wider vision" section; the "standing goal" framing
  and three-path breakdown now live in `VISION.md`'s Pillar 2, the
  correct project-wide home. Updated the three other files that linked
  to the deleted file (`VISION.md`, `photo-server/DEFERRED.md`,
  `picture-handling/TODO.md`) to point at `VISION.md` Pillar 2 instead.
  Audited every other file in every root folder against its own folder's
  stated scope; found no other mismatches. `documentation/`: 39,976 →
  39,215 characters.

## 2026-07-15 (8)

- Untracked 5 `.pyc` files under `app/*/__pycache__/` that were
  committed before `__pycache__/` was added to `.gitignore` last
  entry — `git rm --cached`, files kept on disk. Confirmed via
  `git ls-files -i -c --exclude-standard` that nothing else tracked
  matches any `.gitignore` pattern.
- Researched current CVEs (real web search, not training-data guesses)
  for every package in `requirements.txt`, which had no version pins at
  all, and pinned each to the latest patched release: `Pillow==12.3.0`
  (fixes CVE-2026-25990, CVE-2026-42308, CVE-2026-42309, CVE-2026-55379,
  CVE-2026-55380), `mysql-connector-python==9.7.0` (well past
  CVE-2024-21272 and CVE-2025-21548), `numpy==2.5.1`, `opencv-python==5.0.0.93`
  (bundles a libwebp/libvpx build; 5.0.0.93 is current),
  `exif==1.6.1` and `python-magic==0.4.27` (both already the latest
  release on PyPI — no newer version exists, no known CVEs found for
  either). **Unverified**: this sandbox has no `pip`/`ensurepip`, so
  none of this could actually be installed and run against `app/` —
  numpy 2.x and opencv-python 5.x are major version bumps with real
  breaking-change risk (numpy 2.0's ABI break in particular). Flagged in
  `picture-handling/TODO.md`'s Known Drift for Joakim to verify on a
  machine with pip before trusting it. Also noted, but deliberately not
  acted on (system-level, outside this session's authority per
  POLICY.md): Python 3.12.13 is the current security-patch release for
  this repo's 3.12 branch, vs. the 3.12.3 recorded in
  `photo-server/HARDWARE.md`.
  `documentation/`: 39,441 → 39,976 characters.

## 2026-07-15 (7)

- Added `tools/doc_metrics/`: TDD'd (stdlib `unittest`, pytest isn't
  installed in this environment) character-count logging so the
  character-count-change rule is measured the same way every time
  instead of ad hoc `wc -c`. `metrics.py` counts Unicode codepoints per
  `*.md` file; `log.py` snapshots the current commit (or `--backfill`s
  the full history via read-only `git show`/`git ls-tree`, never
  touching the working tree); `report.py` prints char count, delta, and
  an approximate token count (chars/4, explicitly labeled as directional
  only — real cost also depends on current model pricing, not tracked
  here) per commit. `metrics.jsonl` is git-tracked (the durable record,
  per the self-sufficiency rule); `metrics.db` (SQLite) is gitignored,
  local, and rebuildable from the jsonl via `--rebuild-db`. Backfilled
  all 77 existing commits. Also fixed two `.gitignore` gaps found while
  doing this: `.claude/settings.local.json` was untracked but not
  ignored (risk of accidentally committing local permission config), and
  `__pycache__/` wasn't ignored anywhere. Corrected the character-count
  methodology itself: earlier entries in this file used `wc -c` (byte
  count), which runs ~0.8% high on this repo's docs because of em
  dashes; from here on, counts are Unicode codepoints via this tool —
  noted as a one-time methodology switch, not a discrepancy to chase.
  `documentation/`: 39,113 characters (codepoint count, not directly
  comparable to prior entries' byte counts). `CLAUDE.md`: 6,178
  characters.

## 2026-07-15 (6)

- Captured Joakim's long-term system vision (four pillars: distributed
  storage/DFS with a blockchain-like stability mechanism, metadata/
  search/curation, presentation and event-based sharing with an opt-in
  privilege-for-data-sharing model, and multi-angle event reconstruction)
  in a new project-wide `documentation/VISION.md`, cross-linked from
  `distributed-sync/README.md`, `photo-server/README.md`,
  `photo-server/DPFAS_VISION.md`, and the top-level `documentation/
  README.md` index, rather than duplicated into any of them. Flagged
  Pillar 3's opt-in-sharing model as an open tension against the current
  closed-by-default posture in `POLICY.md`'s open questions. Added the
  Sunday deadline's real context to `photo-server/README.md`: a memorial
  for Per, Elisabeth's mother's late partner, where she wants to pick
  photos from ripped CDs/DVDs for a picture-frame USB stick — this is
  why v1 stops at browse/search/tag/download and nothing more.
  `documentation/`: 33,899 → 39,441 characters.

## 2026-07-15 (5)

- Absorbed two external planning documents (a photo-server build plan and
  a GUI-spec amendment, both supplied in chat) into a new
  `documentation/photo-server/` topic folder: README, TODO (the granular
  TDD roadmap), HARDWARE, DATA_DICTIONARY, DEFERRED, DPFAS_VISION, and
  MOCKUP (bare-minimum login + thumbnail-screen written spec, no code).
  Sequenced the roadmap so login (Phases 0–1) is complete before any
  photo/catalogue work starts, per Joakim's priority. Flagged one
  inference for confirmation: the original `selections` table is treated
  as dropped in favor of the GUI spec's tag-based (`kind='album'`)
  mark/download mechanism, since both solved the same problem — see
  DATA_DICTIONARY.md. Superseded the "first MVP/POC, purpose undefined"
  item and its speculative UI/database/AI sections in
  `picture-handling/TODO.md` with a pointer to the new folder, now that
  the purpose is decided. Added two CLAUDE.md rules: report the
  character-count change for every documentation edit, and tightened
  "Lean and compact" into "Lean, exact, and compact." Done on a new
  `photo-server-planning` branch, not master, per Joakim's request.
  `documentation/`: 8,249 → 33,899 characters. `CLAUDE.md`: 5,624 → 5,986
  characters.

## 2026-07-15 (4)

- Second pass on the same documentation trim, per Joakim's answers to a
  few judgment calls: dropped the "In use?" column from both external-
  tools tables (all rows read "Not yet" — zero information), tightened
  a couple more sentences, and removed the sudo/deployment rule
  restatement from CLAUDE.md's high-blast-radius list in favor of a
  pointer to POLICY.md's "Deployment and system access" section (POLICY.md
  already declares itself the sole home for that rule). Declined:
  merging each topic's README+TODO into one file (keeps the documented
  structure rule intact) and resolving the "4D" placeholder in
  `picture-handling/TODO.md` (still unclear — left as-is).
  8,430 → 8,249 characters in `documentation/`.

## 2026-07-15 (3)

- Trimmed `documentation/` for redundancy: the "roadmap addendum
  expected from Joakim" note was stated near-verbatim in three files
  (distributed-sync README, its TODO, and POLICY.md) — now stated once
  in TODO.md's open question, with the other two pointing at it. Also
  de-duplicated a NAS-spec restatement and a security/privacy-posture
  restatement, and tightened wordy passages in `picture-handling/TODO.md`
  and the top-level `documentation/README.md`. No meaning changed; the
  SETI@home analogy was deliberately kept since it's the origin of the
  idea, not just flavor text. 8,950 → 8,430 characters.

## 2026-07-15 (2)

- Noted the next session's starting point in
  `documentation/picture-handling/TODO.md`: build the first frontend
  MVP/POC, operating on pictures already on this server, for a specific
  purpose still to be defined with Joakim. No code written this session.

## 2026-07-15

- Initialized the working-agreement and documentation structure:
  `CLAUDE.md` (non-negotiables + high-blast-radius definition), root
  `README.md`, `documentation/` (policies, picture-handling,
  distributed-sync), and this changelog. Retired `docs/` and
  `resources/for documentation/`, folding their content into the new
  structure. Done to make the repo self-sufficient for future sessions
  instead of relying on AI memory.
