# First mockup — login screen and thumbnail screen

Written spec only — no HTML/CSS/code produced this session. This is the
bare minimum for each screen: what TODO.md Phases 1 and 4 build toward,
not the full GUI spec (that's tracked separately, see "Full spec" below).
Anything not listed here is deliberately excluded from this first
mockup, with a pointer to the later phase that adds it.

## Login screen

Fields: email, password, submit button. Nothing else.

States:
- Success → redirect to the thumbnail screen's catalogue list.
- Failure (wrong password, unknown email, or malformed input) → one
  generic message, "Incorrect email or password" — identical wording and
  response time target regardless of which of the three caused it, so
  the response never discloses whether an email is registered.
- Locked out (6th failed attempt within a minute, same IP) → "Too many
  attempts, try again in a minute."

Explicitly excluded from this mockup: "remember me", password reset/
forgot-password flow, account self-registration, two-factor auth. None
of these are in the original build plan either — flagging password
reset as a gap worth a decision before Phase 1 ships, since with only
two accounts a lost password currently means Joakim resets it by hand
via the CLI account-creation tool (acceptable at this scale, but should
be a conscious choice, not an oversight).

## Thumbnail screen (catalogue browse, bare minimum)

Given one catalogue: a grid of thumbnails, tappable. Nothing else yet.

Included: catalogue title (full folder name, unmodified, wrapped never
truncated — see DATA_DICTIONARY.md's note on `catalogue`), thumbnail
grid, a placeholder tap target per photo (opens something — full
lightbox behavior is later).

Explicitly excluded from this first mockup, each added in a later
TODO.md phase:
- Persistent top bar showing the active tag/album, count, size, download
  button — added with Phase 5 (tags/albums), since it has nothing to
  show until tags exist.
- Tap-to-add-to-active-tag gesture — same phase, same reason.
- Thumbnail density controls (pinch/Ctrl+scroll + button fallback) —
  cosmetic, added once the base grid works.
- Lightbox, info panel, search/filter panel — later Phase 4/5 sub-steps.

## Full spec

The complete screen behavior (top bar, tap-to-tag, density, lightbox,
info panel, stability rules once Elisabeth has used it) lives in the GUI
spec amendment Joakim provided; its content is distributed across this
file, DATA_DICTIONARY.md, and TODO.md's Phase 4–5 steps rather than kept
as a separate standalone document, per CLAUDE.md's no-duplication rule.
