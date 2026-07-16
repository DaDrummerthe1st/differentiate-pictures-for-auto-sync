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

## Other open items (carried over, not yet done)

- Delete stray leftover zip files sitting in old zipcache docker
  volumes (pre-existing debris from before the caching fix, and from
  before bulk downloads switched away from zips entirely).
- Recheck for anything else possibly missing from the branch-mixup
  incident referenced above.
- If this app is ever shared/open-sourced, re-check this documentation
  and the code for personal/family references (paths, filenames,
  memorial context) that shouldn't be public.
