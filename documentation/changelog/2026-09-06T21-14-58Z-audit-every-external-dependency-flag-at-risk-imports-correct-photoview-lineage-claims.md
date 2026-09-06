# Audit every external dependency, flag at-risk imports, correct PhotoView lineage claims

Full-repo dependency audit after the native-app pivot: every Android/Gradle, Python
(`previous-work/`), Docker, and vendored-AI-model-pick dependency checked against live sources
(GitHub/OSV.dev/PyPI) for license, maintenance activity, and CVE status — not training-data memory
or a self-reported tag. New `documentation/security/DEPENDENCIES.md` catalogs all of it, with
tables split into **last activity date** vs. **activity pattern** (raised by Joakim mid-session:
a recent commit alone can't tell "healthy" apart from "CI bumps land but no real feature has
shipped in years," and the inverse — high PR volume that never merges — is a worse signal than
low-but-landing activity). Confirmed the CI dependency-freshness gap is worse than assumed: a past
commit deleted working pip/uv/docker Dependabot coverage for what's now `previous-work/` instead of
repointing it, and no `gradle` entry exists for `android/` at all — fix recommended, not applied
(config change). Added `DO NOT REMOVE THIS COMMENT UNTIL RESOLVED` markers on every at-risk
dependency line across `android/app/build.gradle.kts`, `previous-work/`'s requirements.txt/
pyproject.toml files, and its Dockerfiles/compose files, each pointing back to DEPENDENCIES.md.
Corrected `mobile/TODO.md`/`GLOSSARY.md`'s PhotoView lineage claim: `chrisbanes/PhotoView` was
never GitHub-archived (transferred to `Baseflow/PhotoView`, dormant since 2022-03-25 — the "archived
Oct 2022" date belonged to an unrelated fork), and the adopted `io.getstream:photoview` fork is
maintained-but-dormant on real library code, not "actively maintained." Two real judgment calls
raised for Joakim rather than guessed: whether the MIT/Apache-2.0-only license bar (currently
documented only for vendored AI models in DETECTORS.md) should extend to general dependencies —
answer pending; and whether to run a live system-inventory scan of the dev machine/hardware repo —
declined, documented state is enough.

- **Doc size**: `security/DEPENDENCIES.md` +20859 (new file); `GLOSSARY.md` +1370;
  `security/TODO.md` +1161; `mobile/TODO.md` +457; `security/README.md` +236. Net +24083 chars.
