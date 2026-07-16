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

## Voiceover durability/export

Current voiceover recordings (audio + pointer-timeline JSON) only work
via this app's own server staying runnable - the referenced photo paths
and the live playback re-composition break if the app changes
significantly or the photo library gets reorganized. Joakim wants
recordings to remain listenable/watchable for years, independent of
this app's future, and shareable (e.g. shown to his kids later).

Decided direction (2026-07-16): **bake each voiceover into an actual
MP4 video** - photos shown full-frame with a moving pointer-dot overlay,
synced to the recorded audio, encoded via ffmpeg. This is the most
durable option (any device/player can open an MP4 forever, fully
independent of this app) versus a self-contained HTML+audio+photos
folder (also considered, more fragile long-term - needs a browser and
working JS forever) or just fixing path-fragility without exporting
(smallest change, doesn't solve the actual "shareable for years" ask).

Not started - needs: ffmpeg added to the Docker image, a frame-plan
function (given events + fps + duration → which photo + pointer
position per frame, pure logic, unit-testable without ffmpeg), a
Pillow-based frame renderer (photo letterboxed to a fixed video
resolution + dot overlay), and the ffmpeg invocation to mux frames +
audio into the final MP4.

## History note: why this project lives in this repo at all

Started as a genuinely separate repo (`~/code/project/mamma-photo-viewer`),
but an accidental concurrent Claude Code session (a VS Code extension bug -
see the GitHub issue filed 2026-07-16 for typing-while-a-popup-opens
spawning a duplicate session) fetched that repo's history into this one
under a same-named branch. Once discovered, Joakim opted to keep building
here rather than untangle it back out.

## Other open items (carried over, not yet done)

- Delete stray leftover zip files sitting in old zipcache docker
  volumes (pre-existing debris from before the caching fix, and from
  before bulk downloads switched away from zips entirely).
- Recheck for anything else possibly missing from the branch-mixup
  incident referenced above.
- If this app is ever shared/open-sourced, re-check this documentation
  and the code for personal/family references (paths, filenames,
  memorial context) that shouldn't be public.
