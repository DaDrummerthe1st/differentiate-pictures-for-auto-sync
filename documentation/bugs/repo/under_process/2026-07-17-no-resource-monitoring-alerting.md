# No resource monitoring / alerting for the deployed stack

Status: **not designed**.

## Background

Raised 2026-07-17 by Joakim while chasing a broken-thumbnail bug on a memory-tight host (3.8GB total, ~1GB "available" under 5 containers - see the `hardware` repo's `server/192.168.1.10/hardware/README.md`, RAM since upgraded to 16GB). Wants periodic system resource levels (RAM, disk, per-container) in the logs, with some kind of flag/alert when something's "topped out" (an actual threshold, not just raw numbers to eyeball).

## Real decisions needed before building

- Where do these logs live - a new table? a file? piggyback on `analytics.db`?
- What counts as "topped" per resource?
- What happens when the threshold trips - just a log line? something that actually notifies Joakim?

Log/monitoring feature, not a quick add.
