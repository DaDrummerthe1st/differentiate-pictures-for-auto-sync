# documentation/policies/

Project-wide policy and cross-cutting-topic docs — not tied to one feature folder.

| File | What's there |
| --- | --- |
| [POLICY.md](POLICY.md) | Hard, project-wide constraints — the one file where "hard rules live here." Named `POLICY.md` rather than `README.md`, a deliberate exception so that's unmistakable. |
| [AUTHENTICATION.md](AUTHENTICATION.md) | Current auth state, remaining hardening priority order, and the OAuth-exclusion decision — applies to both `app/` and `server/`, not one topic folder. |

No `TODO.md` — this folder is reference/decision docs, not a place with its own ongoing implementation work; open auth items live in [AUTHENTICATION.md](AUTHENTICATION.md) itself.
