# Scope pivot: admin photo-source setting + resource benchmarking move to prod /tank, deferred to next session

After Phase 3 (face detection) landed, Joakim redirected the next piece of work: an admin-only,
live/DB-backed "where to load pictures from" setting, plus real per-detector CPU-time benchmarking
per ~100-photo batch. First plan draft wrongly assumed the local workstation dev environment;
corrected to run directly against the home server (`192.168.1.10`) and a new, dedicated
`/tank/dpfas_media` directory (not `/tank/momfiles`, which stays Elisabeth's, untouched) - real
per-detector load numbers need the real hardware. Full design saved to
`documentation/plans/tingly-humming-pudding.md`; deliberately **not implemented this session**
(explicit token-saving instruction) - `documentation/curation/TODO.md` updated with a short pointer
so next session starts there, ahead of Phase 4. Also corrected a process-lapse bug report filed
earlier this session after discovering the exact scenario it describes was already documented in
`documentation/tooling/README.md` from a prior incident - the gap was following that doc, not a
missing rule.

- **Doc size**: `documentation/plans/tingly-humming-pudding.md` +8619 chars.
- **Doc size**: `documentation/curation/TODO.md` +1715 chars.
- **Doc size**: `documentation/bugs/claude-bugs/under_process/2026-08-08-blocked-commit-s-staged-files-bled-into-an-unrelated-follow-up-commit-s-message.md` +937 chars.
