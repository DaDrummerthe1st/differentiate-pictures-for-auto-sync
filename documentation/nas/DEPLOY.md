# Deploy target and process

## Target

`192.168.1.10` — Joakim's real home server. Full hardware/network detail lives in a separate repo, `~/code/resources/hardware/documentation/server/192.168.1.10/` (not cloned into this one — see that repo directly, or ask Joakim, rather than trusting a stale copy pasted in here). As of 2026-09-07: `ubuntu2404lts`, Ubuntu 24.04 LTS, i5-650 (2c/4t, CPU-only), 16GB RAM, ZFS `raidz1` pool at `/tank` (~2.7TB free). SSH user `joakim`, password-auth only (no passwordless key login).

## Hard rule: this session never touches `.10` directly

No SSH, no `ping`, no `curl` against `192.168.1.10` from an AI session — Joakim's explicit instruction, 2026-09-07: security (no unsupervised mistake), staying personally involved in his own infrastructure, and general discomfort with an LLM reaching into his private systems. Every command below is written for **Joakim to run himself**, copyable text only. This generalizes [../policies/POLICY.md](../policies/POLICY.md)'s existing "deployment is always Joakim's job" rule to cover read-only inspection too, not just deploy actions.

## Inventory pass (run by Joakim, 2026-09-07) — real findings, not assumptions

- **Docker is present and current**: 29.8.0, Compose v5.5.1. No install step needed.
- **The old photo-server stack was live at inventory time** — `caddy`, `photo-viewer`, `postgres`, `redis`, `detector` containers all "Up 3 days," actively serving real traffic (`caddy` bound to `0.0.0.0:80`/`:443`), with `auth` crash-looping ("Restarting (3)"). **Retired same day** — see "Old photo-server stack — retired 2026-09-07" below.
- **Ports**: `22` (SSH), `25` (Postfix mail, loopback-only) remain. `80`/`443` are now free following the retirement below — no live Caddy config to work around anymore.
- **Existing checkout**: `/home/joakim/differentiate-pictures-for-auto-sync` is the live deployed checkout that stack runs from. The NAS's fresh code needs its own separate directory on `.10` — never this one.
- **Real, live data already exists on this box**: a `differentiate-pictures-for-auto-sync_postgres_data` Docker volume backing the live stack, plus `/tank` (2.65TB free of 3.6TB) and a separate `/media/master_copy` NTFS backup (497GB free). **None of this is "clean slate" territory** — clean-slate applies to the NAS's own fresh code/schema, never to this pre-existing live data; nothing in this design touches that volume.

## Old photo-server stack — retired 2026-09-07

Confirmed obsolete and taken down by Joakim, same day: `docker compose down` from `/home/joakim/differentiate-pictures-for-auto-sync` removed all 6 containers (`caddy` included — the reverse proxy itself, not just the backend services) and the project's Docker network. Verified externally: `photos.reuterborg.se` now fails to connect in a browser, as expected. `80`/`443` are free; the crash-looping `auth` container is gone with it, moot rather than fixed.

**Not removed, deliberately**: the underlying volumes (`differentiate-pictures-for-auto-sync_postgres_data`, `_caddy_data` holding the Let's Encrypt cert, etc.) — `docker compose down` without `-v` leaves them on disk, dormant. Real data (the old photo library's database) lived in that volume; nothing here suggests deleting it, that stays Joakim's own call if it's ever needed.

## Network exposure — LAN + WireGuard, no public hostname

Decided 2026-09-07 — see [ARCHITECTURE.md](ARCHITECTURE.md)'s "Network exposure" section for the reasoning. The NAS is reachable on the home LAN directly, and off-LAN only through the existing WireGuard tunnel — no public hostname, no Caddy site block needed, no Let's Encrypt cert needed. This also fully resolves the earlier port-collision question: no public port is claimed at all.

## `nas/deploy.sh`

A script Joakim runs from his own machine — never executed by this session. What it's expected to do:

1. Build the `nas/backend` and `nas/frontend` Docker images locally, or on `.10` directly via a remote build context.
2. `rsync`/`scp` the built artifact (or the repo checkout) to a new, separate directory on `.10` — not `/home/joakim/differentiate-pictures-for-auto-sync`.
3. Run `docker compose up -d --build` on `.10` over SSH, binding only to the LAN interface (or `10.10.10.1`, the WireGuard tunnel address) — never `0.0.0.0` on a port meant to stay off the public internet.
4. Print the resulting LAN URL (`https://192.168.1.10:<port>`) for Joakim to open and check by hand.

Not written yet — one small open item remains: the actual port number and cert approach (self-signed vs. a local CA Joakim already trusts on his devices), neither of which is a live-production-touching decision anymore now that exposure is LAN/VPN-only.

## Status

Opened 2026-09-07. Real inventory findings and the LAN-only exposure decision folded in same-day. `deploy.sh` still not written, pending the port/cert choice above.
