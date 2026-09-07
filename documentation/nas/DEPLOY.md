# Deploy target and process

## Target

`192.168.1.10` — Joakim's real home server. Full hardware/network detail lives in a separate repo, `~/code/resources/hardware/documentation/server/192.168.1.10/` (not cloned into this one — see that repo directly, or ask Joakim, rather than trusting a stale copy pasted in here). As of 2026-09-07: `ubuntu2404lts`, Ubuntu 24.04 LTS, i5-650 (2c/4t, CPU-only), 16GB RAM, ZFS `raidz1` pool at `/tank` (~2.7TB free). SSH user `joakim`, password-auth only (no passwordless key login).

## Hard rule: this session never touches `.10` directly

No SSH, no `ping`, no `curl` against `192.168.1.10` from an AI session — Joakim's explicit instruction, 2026-09-07: security (no unsupervised mistake), staying personally involved in his own infrastructure, and general discomfort with an LLM reaching into his private systems. Every command below is written for **Joakim to run himself**, copyable text only. This generalizes [../policies/POLICY.md](../policies/POLICY.md)'s existing "deployment is always Joakim's job" rule to cover read-only inspection too, not just deploy actions.

## Inventory pass (2026-09-07, before assuming anything about what's already on `.10`)

Ran by Joakim, not this session — output not yet known at doc-write time. Covers: Docker presence/version, running containers/images/volumes, project-related systemd services, listening ports, ZFS status, disk space, any existing checkout of this repo or the old photo-server, crontab. **Fold real findings in here once available — don't leave this section's assumptions (e.g. "Docker is very likely already installed, since the old photo-server ran there") unconfirmed for long.**

## `nas/deploy.sh`

A script Joakim runs from his own machine — never executed by this session. What it's expected to do, once the inventory pass above confirms the target environment:

1. Build the `nas/backend` and `nas/frontend` Docker images locally (or on `.10` directly via a remote build context — TBD once Docker's actual presence on `.10` is confirmed).
2. `rsync`/`scp` the built artifact (or the repo checkout) to `.10`.
3. Run `docker compose up -d --build` on `.10` over SSH, in a directory dedicated to this project (not overlapping whatever the old photo-server prototype left behind, until the inventory pass confirms what that is).
4. Print the resulting service URL (`https://192.168.1.10:<port>` or similar) for Joakim to open and check by hand.

Not written yet — blocked on the inventory pass above so the script's assumptions (Docker present? which port is free? does an old `postgres` volume already exist and need a decision, not a silent overwrite?) are based on the real box, not a guess.

## Status

Opened 2026-09-07. Inventory commands handed to Joakim; `deploy.sh` itself not yet written, pending that output.
