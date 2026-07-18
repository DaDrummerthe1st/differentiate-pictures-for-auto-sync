# TODO — documentation/gui/

## Next phase: login/authentication

Currently no-login by design (LAN-only, single-household, one-off use
case). Before this app is used by multiple people or leaves the LAN,
add a proper login layer. Requirements as given:

- **Passkeys** as the primary login method (WebAuthn), not just
  password-based auth.
- **Session hijacking protection**: secure, httpOnly, SameSite cookies
  for session tokens; rotate session identifiers on login; consider
  binding sessions to IP/user-agent fingerprint with re-auth on
  mismatch.
- **Real TLS**, not the current self-signed cert (e.g. via a reverse
  proxy with a proper certificate, or a local CA the household trusts) -
  needed once this isn't purely LAN-local.
- **Password length requirement only** - no composition rules (no
  forced mix of uppercase/digits/symbols). This matches current
  NIST guidance and avoids pushing users toward predictable patterns.
- **Reject known-breached passwords** (e.g. check against
  Have I Been Pwned's range API or an equivalent offline breached-
  password list) so a legitimate user isn't tempted to reuse an old,
  already-leaked password just because it's convenient - the login
  flow needs to stay easy enough (passkeys, password manager-friendly)
  that reuse is never the path of least resistance.
- **Per-user isolation of PII**: each user should only ever see their
  own photos/stories/voiceovers once multi-user support exists, not a
  shared pool.

Not started - no code, no design doc yet. Flagged by Joakim on
2026-07-16 as the deliberate next step after the current no-login
single-user version is done.

### Starting this work: read first, then resolve the open question below

**Purpose, stated plainly so it doesn't get lost in the mechanics below**:
next session's job is to merge `phase-1-login`, `mamma-photo-viewer`, and
`master` into one working system, not just land isolated features. The
result has to hit both bars at once — good UX (this is still Elisabeth's
mum's app, ease of use hasn't stopped mattering) and genuinely high
security, because this is becoming Joakim's own real server, not a
one-off LAN tool scoped to a single Sunday. Treat the security
requirements below (passkeys, session-hijacking protection, real TLS,
breach-password checks, per-user isolation) as the actual bar, not
aspirational — closer to buzzkit's production rigor than the current
no-login LAN-only posture.

- [CLAUDE.md](../../CLAUDE.md) (working agreement), [POLICY.md](../policies/POLICY.md).
- [photo-server/README.md](../photo-server/README.md)'s Status section: the
  *backend* login-architecture decision is already made and executed
  (`phase-1-login` branch, steps 1.1–1.8 done) — ported from Joakim's
  existing buzzkit login implementation (argon2id, JWT access+refresh via
  redis). That question is resolved, don't re-ask it.

**Genuinely open** — this GUI (`app/`, Flask) is a separate codebase from
the photo-server backend (`server/`, FastAPI) — resolve before writing
any code: does GUI login mean (a) adapting the same ported approach
directly onto `app/`, or (b) `app/` eventually authenticating against
the `server/` backend instead of implementing its own auth? Ask Joakim,
don't assume.

**Branch state** (measured 2026-07-17, current commit on
`mamma-photo-viewer` was `a7d72d5` — re-check `git log`/`git status` if
stale):
- `phase-1-login`: 18 ahead / 0 behind `master` — backend login done
  through step 1.8, clean, no catch-up needed to merge.
- `mamma-photo-viewer` (this branch): 22 ahead / 134 behind `master` —
  needs `master` merged in first, per [CLAUDE.md](../../CLAUDE.md)'s
  merge procedure (merge target → feature branch first, resolve
  conflicts there, only then feature → target).
- `md5_duplicate_drop`, `photo-server-planning`: 0 ahead of `master`,
  stale — not merge candidates, just old branches to confirm-then-delete
  with Joakim.

Per [CLAUDE.md](../../CLAUDE.md)'s branching rules: ask before starting
on a new branch vs. continuing here, and get explicit confirmation
before any merge into `master`, every time.

## Voiceover feature

Moved to its own subfolder: [voiceover/README.md](voiceover/README.md)
(how it works today) and [voiceover/TODO.md](voiceover/TODO.md) (the
planned MP4-export work) — substantial enough a feature to warrant its
own doc root rather than living inline here.

## History note: why this project lives in this repo at all

Started as a genuinely separate repo (`~/code/project/mamma-photo-viewer`),
but an accidental concurrent Claude Code session (a VS Code extension bug -
see the GitHub issue filed 2026-07-16 for typing-while-a-popup-opens
spawning a duplicate session) fetched that repo's history into this one
under a same-named branch. Once discovered, Joakim opted to keep building
here rather than untangle it back out.

## History note: why bulk downloads are sequential, not a zip

Originally "download all"/"download selected" built one zip server-side,
then streamed it. Switched away from this 2026-07-16 after mum's actual
download over real (slow, USB-drive-destination) conditions showed the
real problems: a single zip is all-or-nothing (any interruption loses
the whole batch), gives no real progress feedback until fully built, and
can't be cancelled cleanly. Per-file sequential transfer (now used by
both buttons) shows honest incremental progress, survives individual
file failures, and can be cancelled without losing anything already
saved. Confirmed as a permanent decision (not just a workaround) the
same day - the zip endpoint (`POST /api/zip`), its client-side code, and
its tests were removed entirely rather than left dormant.

## Analytics log format — more narrative, less terse

Idea floated by Joakim 2026-07-17, not decided or started: today's
`_log_event()` rows are terse structured fields (event type + a short
detail string, e.g. `download_zip_done count=12`). Over many iterations
of this app, terse IDs stop being legible on their own (`"#12345 opened
by #22345 zoomed in"`). Direction being considered: freetext-style log
lines that stay self-explanatory read cold, e.g. `"User #12345 opened
picture #2344554 and spent 234 secs zooming and pressing buttons"`.
Trade-off not yet weighed: more legible over time vs. harder to query/
aggregate than structured fields. Needs a design decision (keep
structured fields and add a rendered freetext view, or replace the
stored format outright) before any implementation — TDD applies as
usual once decided.

## Open from the 2026-07-18 session

- **Download-folder UX rework, designed, not built**: remove the
  upfront "choose folder" screen (currently shown before the gallery,
  blocking first use). Instead: go straight to the gallery; prompt for
  a folder lazily, only on the first actual save action; bake the
  current-folder indicator into the toolbar's existing
  `downloadFolderLabel` sentence ("Bilder sparas i: ..." /
  "Nedladdningar sparas enligt webbläsarens nedladdningsinställning"),
  made clickable/hoverable to show the full path and let the user
  re-pick. TDD-ready now that the test-tool decision below is made.
- **Decided 2026-07-18: Selenium, not Playwright** — per
  `POLICY.md`'s new vendor-lock-in-and-openness principle (prefer
  vendor-neutral tools; Playwright is Microsoft-driven, Selenium is a
  W3C standard with no single owner). Selenium's usual downsides
  (verbose API, historically flakier waits) matter less here than
  usual: this app's test surface is small, and the File System Access
  API it depends on is Chromium-only anyway (Firefox already gets a
  documented fallback), so there's no real cross-browser-coverage
  benefit from Playwright being given up. Containerized only
  (`POLICY.md`'s no-system-installs rule) - `selenium/standalone-chrome`
  is the equivalent of the Playwright image previously considered.
- **Thumbnail pre-compile design synthesis** - see
  `../bugs/reports/2026-07-17-pre-compile-thumbnails-ahead-of-time.md`,
  updated 2026-07-18 with a concrete design from Joakim's answers
  (versioned cache path, one idempotent `ensure_thumbnail` method
  serving manual backfill + on-demand fallback + any future event
  trigger). Still needs Joakim's sign-off on the synthesis before
  building.
- **Grid pagination**, a separate/complementary idea to pre-compiling -
  see `../bugs/reports/2026-07-18-paginate-the-grid-instead-of-loading-all-thumbnails-at-once.md`.
  Candidate, not evaluated.
- **Lightbox bug, not root-caused** - see
  `../bugs/reports/2026-07-18-lightbox-shows-previous-photo-when-clicking-a-not-yet-loaded-thumbnail.md`.
  Symptom changed after today's redeploy (now shows nothing instead of
  the previous photo) - needs a live repro with DevTools open, not more
  static code reading.

## Other open items (carried over, not yet done)

- Recheck for anything else possibly missing from the branch-mixup
  incident referenced above.
- If this app is ever shared/open-sourced, re-check this documentation
  and the code for personal/family references (paths, filenames,
  memorial context) that shouldn't be public.
