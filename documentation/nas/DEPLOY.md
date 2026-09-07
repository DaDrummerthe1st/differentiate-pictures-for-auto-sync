# Deploy target and process

## Target

`192.168.1.10` — Joakim's real home server. Full hardware/network detail lives in a separate repo, `~/code/resources/hardware/documentation/server/192.168.1.10/` (not cloned into this one — see that repo directly, or ask Joakim, rather than trusting a stale copy pasted in here). As of 2026-09-07: `ubuntu2404lts`, Ubuntu 24.04 LTS, i5-650 (2c/4t, CPU-only), 16GB RAM, ZFS `raidz1` pool at `/tank` (~2.7TB free). SSH user `joakim`, password-auth only (no passwordless key login).

## Hard rule: this session never touches `.10` directly

No SSH, no `ping`, no `curl` against `192.168.1.10` from an AI session — Joakim's explicit instruction, 2026-09-07: security (no unsupervised mistake), staying personally involved in his own infrastructure, and general discomfort with an LLM reaching into his private systems. Every command below is written for **Joakim to run himself**, copyable text only. This generalizes [../policies/POLICY.md](../policies/POLICY.md)'s existing "deployment is always Joakim's job" rule to cover read-only inspection too, not just deploy actions.

## Inventory pass (run by Joakim, 2026-09-07) — real findings, not assumptions

- **Docker is present and current**: 29.8.0, Compose v5.5.1. No install step needed.
- **The old photo-server stack is still live in production, not decommissioned** — `caddy`, `photo-viewer`, `postgres`, `redis`, `detector` containers all "Up 3 days," actively serving real traffic (`caddy` is bound to `0.0.0.0:80`/`:443`, almost certainly what `photos.reuterborg.se` resolves to). **`auth` is crash-looping** ("Restarting (3)") — a live, currently-broken piece of that real service, unrelated to this NAS design work and out of scope for this session to touch or fix.
- **Ports already taken**: `22` (SSH), `25` (Postfix mail), `80`/`443` (Caddy, the live stack). The fresh NAS app needs a different port, or its own Caddy site block on the existing reverse proxy — the latter means editing a live production config, Joakim's call, not drafted blind here.
- **Existing checkout**: `/home/joakim/differentiate-pictures-for-auto-sync` is the live deployed checkout that stack runs from. The NAS's fresh code needs its own separate directory on `.10` — never this one.
- **Real, live data already exists on this box**: a `differentiate-pictures-for-auto-sync_postgres_data` Docker volume backing the live stack, plus `/tank` (2.65TB free of 3.6TB) and a separate `/media/master_copy` NTFS backup (497GB free). **None of this is "clean slate" territory** — clean-slate applies to the NAS's own fresh code/schema, never to this pre-existing live data; nothing in this design touches that volume.

## `nas/deploy.sh`

A script Joakim runs from his own machine — never executed by this session. What it's expected to do, now that the inventory above is real:

1. Build the `nas/backend` and `nas/frontend` Docker images locally, or on `.10` directly via a remote build context.
2. `rsync`/`scp` the built artifact (or the repo checkout) to a new, separate directory on `.10` — not `/home/joakim/differentiate-pictures-for-auto-sync`.
3. Run `docker compose up -d --build` on `.10` over SSH, using a port the live stack isn't already on (not `80`/`443`/`22`/`25`) — exact port/subdomain choice still open, Joakim's call.
4. Print the resulting service URL for Joakim to open and check by hand.

Not written yet — the remaining open call is the port/subdomain choice (a fresh Caddy site block on the existing reverse proxy vs. a bare port), which is Joakim's decision given it touches live production routing.

## Status

Opened 2026-09-07. Real inventory findings folded in same-day. `deploy.sh` still not written, pending the port/subdomain decision above.
