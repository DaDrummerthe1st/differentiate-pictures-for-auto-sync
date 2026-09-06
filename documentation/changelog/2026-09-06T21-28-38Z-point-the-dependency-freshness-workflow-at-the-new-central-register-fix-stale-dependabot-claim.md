# Point the dependency-freshness workflow at the new central register, fix stale Dependabot claim

Joakim asked whether future sessions would actually stay aware of this session's dependency
findings and keep consulting the central register — checking honestly found a real gap:
WORKFLOW.md's "Dependency freshness" section (what CLAUDE.md itself points dependency work at)
never mentioned [security/DEPENDENCIES.md](../security/DEPENDENCIES.md), and was itself stale —
it still claimed Dependabot covers `pip`/`uv`/`docker` for `root`/`server/`/`detector/`, which the
dependency audit found doesn't exist post-pivot. Fixed both: added an explicit "check
DEPENDENCIES.md before adding any dependency, update it in the same pass" rule, named the
`DO NOT REMOVE THIS COMMENT UNTIL RESOLVED` markers as confirmed unresolved flags, and corrected
the Dependabot coverage claim to say plainly that it currently covers almost nothing.

- **Doc size**: `WORKFLOW.md` +1316.
