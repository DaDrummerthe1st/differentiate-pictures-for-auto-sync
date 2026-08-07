# Role-based tag visibility and a containerized detector service skeleton (build-plan Phase 0-1)

First two phases of curation/TODO.md's new automatic-tagging build plan, scoped down live to just
these two ("only do phase 0 and 1 in this session"). Phase 0: JWTs now carry a `role` claim
(`member`|`admin`, fail-closed default), and `app/main.py`'s tag-listing endpoints use it so a
detected (`source='auto'`) tag is visible to every account regardless of who wrote it, while an
admin sees every manual tag too — built as roles, not hardcoded accounts, per Joakim's explicit
correction. Phase 1: a new `detector/` FastAPI container (skeleton, `GET /health` only) wired into
`docker-compose.yml`, internal-network-only, the future home for the CV/ONNX models themselves so
their footprint stays out of the main app's image. Both build+test-verified locally (server/ and
app/ suites green, detector's image built and reachability-smoke-tested, then torn down). Full
handoff for next session's Phase 2 in curation/TODO.md.

- **Doc size**: `documentation/GLOSSARY.md` +1310 chars.
- **Doc size**: `documentation/curation/DETECTORS.md` +1495 chars.
- **Doc size**: `documentation/curation/RESEARCH_QUEUE.md` +247 chars.
- **Doc size**: `documentation/curation/TODO.md` +1874 chars.
- **Doc size**: `documentation/gui/TODO.md` +2290 chars.
- **Doc size**: `documentation/tags/SCHEMA.md` +2175 chars.
