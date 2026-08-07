# Bump python-multipart to clear the 14 remaining Dependabot alerts

Of the 50 vulnerabilities Dependabot found right after being enabled this session, 36 (all `pillow`)
were already resolved by the earlier same-session version bump. The remaining 14 were all
`python-multipart==0.0.20` in both `requirements.txt` and `detector/requirements.txt` — seven
distinct advisories (GHSA-5rvq-cxj2-64vf, GHSA-v9pg-7xvm-68hf, GHSA-6jv3-5f52-599m,
GHSA-vffw-93wf-4j4q, GHSA-pp6c-gr5w-3c5g, GHSA-mj87-hwqh-73pj, GHSA-wp53-j4wj-2cfg — DoS via
quadratic-time parsing, unbounded header/preamble buffering, parameter smuggling, and an
arbitrary-file-write under non-default config), all fixed by versions between 0.0.22 and 0.0.31.
Bumped to 0.0.32 (current PyPI release, past every patched threshold), full suite (111 tests)
re-verified green first. This repo's Dependabot alert count should read 0 open once GitHub
re-scans this push.

- **Doc size**: none (no `*.md` files touched).
