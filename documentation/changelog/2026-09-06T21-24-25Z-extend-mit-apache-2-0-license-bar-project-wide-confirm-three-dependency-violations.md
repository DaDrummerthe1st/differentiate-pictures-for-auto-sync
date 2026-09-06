# Extend MIT/Apache-2.0 license bar project-wide, confirm three dependency violations

Joakim resolved the license-bar-scope question the dependency audit raised
([DEPENDENCIES.md](../security/DEPENDENCIES.md)): "mit/apache goes for everything we do." Recorded
as a hard constraint in [POLICY.md](../policies/POLICY.md)'s Licensing section (previously the bar
only lived in DETECTORS.md, scoped to vendored AI models). This confirms three dependencies as
actual policy violations rather than just documented facts: `junit:junit:4.13.2` (EPL-1.0,
`android/`, test-only), `psycopg[binary]` (LGPL-3.0, superseded `previous-work/`), and
`mysql-connector-python` (GPL-2.0 + Oracle's FOSS exception, superseded `previous-work/`). Verified
(not assumed) that JUnit5/Jupiter — the obvious JUnit4 replacement — is itself EPL-2.0, so it isn't
a compliant swap; a real MIT/Apache-2.0 Android test framework needs its own research pass before
anything gets replaced. Updated DEPENDENCIES.md, POLICY.md, security/TODO.md, and the three inline
`DO NOT REMOVE THIS COMMENT UNTIL RESOLVED` code comments to reflect confirmed-violation status.
No dependency was actually replaced in this pass — remediation plans remain open TODOs.

- **Doc size**: `POLICY.md` +975; `security/DEPENDENCIES.md` +852; `security/TODO.md` +234.
  Net +2061 chars.
