# First mockup — login screen and thumbnail screen

Written spec only — no HTML/CSS/code produced this session. This is the bare minimum for each screen: what TODO.md Phases 1 and 4 build toward, not the full GUI spec (that's tracked separately, see "Full spec" below). Anything not listed here is deliberately excluded from this first mockup, with a pointer to the later phase that adds it.

## Login screen

Fields: email, password, submit button. Nothing else.

States:
- Success → redirect to the thumbnail screen's catalogue list.
- Failure (wrong password, unknown email, or malformed input) → one generic message, "Incorrect email or password" — identical wording and response time target regardless of which of the three caused it, so the response never discloses whether an email is registered.
- Locked out (6th failed attempt within a minute, same IP) → "Too many attempts, try again in a minute."

Explicitly excluded from this mockup: "remember me", self-service forgot-password (email-based reset conflicts with this project's no-cloud-APIs rule unless a self-hosted SMTP relay is deployed — deferred indefinitely, decided 2026-07-16), account self-registration, two-factor auth.

## Admin password reset screen

Decided 2026-07-16, replacing the earlier "reset by hand via CLI" note: an in-app, admin-only reset — no email involved.

Fields: for each account (both are always listed — there are only ever two), an email/role label and a "Reset password" button. Nothing else.

States:
- Only visible to the admin role; a member account never sees this screen or button. Non-admin hitting the underlying endpoint directly → 403.
- Clicking "Reset password" → a confirm dialog, "Reset password for {email}? This immediately invalidates their current password and logs them out of all sessions." with Confirm/Cancel.
- Confirm → the server generates a new random password, shown exactly once in a copyable text field with the message "Share this with {email} directly — it will not be shown again." and a "Done" button that clears it from the screen (and from any client-side state — never cached, never re-shown).
- A "Done" tap returns to the plain account list (first state).
- Failure (network/server error) → generic "Something went wrong, try again" — no partial state, no password shown.

Explicitly excluded: email delivery of any kind, letting the admin choose their own replacement password (always server-generated, to guarantee entropy), self-service reset by a non-admin (must always go through the admin).

## Thumbnail screen (catalogue browse, bare minimum)

Given one catalogue: a grid of thumbnails, tappable. Nothing else yet.

Included: catalogue title (full folder name, unmodified, wrapped never truncated — see DATA_DICTIONARY.md's note on `catalogue`), thumbnail grid, a placeholder tap target per photo (opens something — full lightbox behavior is later).

Explicitly excluded from this first mockup, each added in a later TODO.md phase:
- Persistent top bar showing the active tag/album, count, size, download button — added with Phase 5 (tags/albums), since it has nothing to show until tags exist.
- Tap-to-add-to-active-tag gesture — same phase, same reason.
- Thumbnail density controls (pinch/Ctrl+scroll + button fallback) — cosmetic, added once the base grid works.
- Lightbox, info panel, search/filter panel — later Phase 4/5 sub-steps.

## Full spec

The complete screen behavior (top bar, tap-to-tag, density, lightbox, info panel, stability rules once Elisabeth has used it) lives in the GUI spec amendment Joakim provided; its content is distributed across this file, DATA_DICTIONARY.md, and TODO.md's Phase 4–5 steps rather than kept as a separate standalone document, per CLAUDE.md's no-duplication rule.
