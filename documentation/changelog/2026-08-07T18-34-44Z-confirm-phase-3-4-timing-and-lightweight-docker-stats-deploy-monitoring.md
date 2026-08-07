# Confirm Phase 3-4 timing and lightweight docker-stats deploy monitoring

Joakim raised two forward-looking asks mid-session (wanting to see workstation load while models
tag, and to deploy to `.10` with monitoring/logging). Resolved both via AskUserQuestion rather than
guessing: session scope stays at Phase 2 (quality trio has near-zero CPU cost, nothing meaningful to
observe yet — Phase 3/4's real ONNX models are next session's start, load-observation goes with
them); Phase 7's deploy monitoring will be lightweight periodic `docker stats` logging to a file, not
a Prometheus/Grafana stack, per the resource-efficiency constraint on the home box's hardware.
Neither is built yet — recorded in curation/TODO.md for whichever session reaches Phase 3/4 and 6/7.

- **Doc size**: `documentation/curation/TODO.md` +692 chars.
