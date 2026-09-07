# Open documentation/nas/: NAS server-side architecture, sync contract, deploy target

New session, own worktree/branch to avoid colliding with the concurrently-active mobile-app session. Designed the NAS as a standalone peer (own PWA, not just a phone backend), a draft bidirectional phone↔NAS sync contract (device pairing, user-controlled sync priority, confidence-driven pull), and the `192.168.1.10` deploy target — with a hard rule that this session never SSHes or deploys there itself, only writes copyable commands for Joakim. Flagged one open policy tension (pilot-usage-learning vs. no-telemetry) in `POLICY.md` rather than resolving it silently.

- **Doc size**: +20168 chars (5 new files under `documentation/nas/`), +165 `documentation/README.md`, +661 `documentation/policies/POLICY.md`, +596 `documentation/GLOSSARY.md`. Total +21590 chars.
