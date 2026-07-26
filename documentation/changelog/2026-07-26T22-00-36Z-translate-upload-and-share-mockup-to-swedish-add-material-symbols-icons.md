# Translate upload-and-share mockup to Swedish, add Material Symbols icons

Joakim asked for the prototype to match the real app more closely: all UI text in Swedish (matching `app/static/index.html`'s `lang="sv"` convention) and the vendored Material Symbols icon library (self-hosted, no CDN, copied from `app/static/vendor/`) applied through the sharing flow specifically — terms toggle (lock/public), method icons (share sheet/person/mail), accept/decline/revoke, pending inbox. Verified with the same headless-Chrome Selenium run (assertions updated for the Swedish strings): 15/15 checks still pass, no console errors, icon glyphs render correctly (not literal text).

- **Doc size**: no `*.md` files touched this pass — prototype code only.
