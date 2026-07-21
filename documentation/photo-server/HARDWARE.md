# Hardware — photo-server

The machine this runs on. It also hosts the ZFS pool other things depend on, so photo-server is containerized (Docker Compose) rather than installed natively — a native install's dependencies could collide with, or need root access shared with, whatever else already runs against that pool. See [README.md](README.md) for the resulting non-negotiable.

| Component | Spec |
| --- | --- |
| CPU | Intel i5-650, 2 cores / 4 threads, 3.2GHz |
| RAM | 3.8GB total, ~1.3GB free at idle |
| GPU | NVIDIA GeForce 210 — not usable for AI, treat the server as CPU-only |
| Storage | 3.6TB ZFS pool at `/tank`, 2.7TB free |
| OS | Ubuntu 24.04 LTS, Python 3.12.3 |
| LAN address | 192.168.1.10, under Joakim's desk |
| SSH user | `joakim` |
| Router | Ubiquiti EdgeRouter X, firmware 3.0.1 (Joakim, 2026-07-17) — LAN gateway `192.168.1.1`. Port-forwarding 80/443 -> 192.168.1.10 needed for the photo-server P0 deploy; see [DEPLOYMENT.md](DEPLOYMENT.md) and CHANGELOG for current status — don't assume done, this drifted stale once already (2026-07-17: an SSH-based attempt to set it silently failed since SSH wasn't enabled on the router yet, and the doc briefly said "configured" when it wasn't). |
| Switch | Linksys LGS1xx-series (unmanaged — no web UI, no port-level software diagnostics), between the server and the router — the server does **not** plug directly into the EdgeRouter. Found 2026-07-18 during an outage investigation this table didn't previously document at all: the switch had run continuously for "probably a couple of years" with no reboot and got into a stuck port state (`NO-CARRIER` on the server's NIC); a power cycle fixed it immediately. See `documentation/bugs/repo/fixed/2026-07-18-photos-reuterborg-se-unreachable-SOLVED.md`. Worth a periodic preventative reboot given this history — not automated, no schedule set. |

The `192.168.1.1` gateway address is inferred from the dev workstation's own `ip route` (same `192.168.1.0/24` subnet as the server) — not read directly off the server or the router itself, per the "physically separate machine" note below. Confirm on the server directly (`ip route | grep default`) if this ever needs to be certain rather than inferred.

**Router admin UI has no valid TLS** (noted 2026-07-17): `https://192.168.1.1` does not present a trusted certificate — expected for a home router's self-managed admin interface, LAN-only exposure, not something to "fix." Flagging so a future session doesn't mistake it for a live problem.

**DDoS / resource-exhaustion risk accepted, not mitigated** (2026-07-17): raised while setting up the P0 internet exposure — a real volumetric DDoS can't be stopped by anything configurable on an EdgeRouter X or in this app; that needs upstream mitigation (ISP-level, or a CDN in front), out of scope for this project's closed/no-cloud-APIs posture. Accepted as a standing risk of self-hosting on a residential line at v1 scale, not a today-fix. What IS mitigated: 2026-07-17's auth-gating work means almost every resource-expensive route (thumbnails, downloads, the full filesystem tree walk) requires a valid session, closing off anonymous abuse of those specifically — see DEFERRED.md for the two routes that remain anonymously reachable and why they're low-risk.

**This is a physically separate machine from wherever an AI session (or Joakim) edits code or runs a dev shell.** Confirmed 2026-07-15: dev/build work (including any Claude Code session) happens on a different Ubuntu machine; only the table above describes 192.168.1.10 itself. Don't infer which host you're on from `uname`/OS match alone — check the IP or ask.

**RAM upgrade still not installed, confirmed 2026-07-18**: `free -h` run live on the server during today's outage investigation still shows `3.8Gi` total — same as the pre-upgrade figure above, so the ordered upgrade has not been installed yet (or at least hadn't as of today). The memtest gate below remains in force. Do not run `docker compose up` against this host until the upgrade is installed and memtested (Memtest86+, at least one full pass) — build and test images on a dev machine until then, per TODO.md.

**Gate knowingly overridden, 2026-07-17**: the memtest gate above is still the standing rule and still applies going forward — it was NOT cleared, the RAM sticks are ordered/paid but not yet installed (expected early the following week). Joakim made an explicit, informed call to run `docker compose -f docker-compose.prod.yml up -d` on this host today anyway, ahead of a hard external deadline, accepting the OOM/instability risk on 3.8GB RAM under five services (Caddy, photo-viewer, auth, Postgres, Redis — the compose file's `mem_limit`s cap worst case at ~1.2GB combined, but that's still tight headroom on this box). This is a one-time, dated exception, not a retroactive removal of the gate — the gate re-applies to any future `docker compose up` on this host once this deploy is torn down or once the RAM arrives, whichever a session should re-verify rather than assume.
