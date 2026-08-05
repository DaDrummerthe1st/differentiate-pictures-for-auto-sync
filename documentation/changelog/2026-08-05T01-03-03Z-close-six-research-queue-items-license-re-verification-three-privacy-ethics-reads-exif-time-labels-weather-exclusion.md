# Close six research-queue items: license re-verification, three privacy/ethics reads, EXIF time labels, weather exclusion

Picked six `RESEARCH_QUEUE.md` items scoped to verification/reads (not a new detector-area survey,
per the project's "one area per session" cadence): independently re-checked every current
DETECTORS.md model pick against its own LICENSE file/model card; ran privacy/ethics reads on
age/gender estimation (substantially de-risked under GDPR Article 9's purpose-based interpretation),
OCR-in-frame (explicit data-minimization requirement now on record), and "best shot"/attractiveness
scoring (bias risk confirmed against real literature, decision left to Joakim); resolved EXIF-derived
time labels to a buildable design needing no model; closed weather-at-capture as excluded. Full
report: `2026-08-05-license-reverification-and-privacy-reads.md` in the `research-findings` repo.
Also filed and fixed an AI-session process lapse (a manual `commit_cost` catch-up commit accidentally
swept in an already-staged real doc commit, mislabeling its history) — see
[documentation/bugs/claude-bugs/fixed/2026-08-05-doc-content-changes-bundled-into-a-mislabeled-commit-cost-catch-up-commit.md](../bugs/claude-bugs/fixed/2026-08-05-doc-content-changes-bundled-into-a-mislabeled-commit-cost-catch-up-commit.md).

- **Doc size**: `documentation/curation/DETECTORS.md` — +5916 chars; `documentation/curation/RESEARCH_QUEUE.md` — +2293 chars; `documentation/GLOSSARY.md` — +5369 chars; `documentation/tooling/README.md` — +689 chars (all Unicode codepoints, per DOC_METRICS.md methodology).
