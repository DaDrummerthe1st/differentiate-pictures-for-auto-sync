# Hardware — photo-server

The machine this runs on. It also hosts the ZFS pool other things depend
on, so photo-server is containerized (Docker Compose) rather than
installed natively — a native install's dependencies could collide with,
or need root access shared with, whatever else already runs against that
pool. See [README.md](README.md) for the resulting non-negotiable.

| Component | Spec |
| --- | --- |
| CPU | Intel i5-650, 2 cores / 4 threads, 3.2GHz |
| RAM | 3.8GB total, ~1.3GB free at idle |
| GPU | NVIDIA GeForce 210 — not usable for AI, treat the server as CPU-only |
| Storage | 3.6TB ZFS pool at `/tank`, 2.7TB free |
| OS | Ubuntu 24.04 LTS, Python 3.12.3 |
| LAN address | 192.168.1.10, under Joakim's desk |

**This is a physically separate machine from wherever an AI session (or
Joakim) edits code or runs a dev shell.** Confirmed 2026-07-15: dev/build
work (including any Claude Code session) happens on a different Ubuntu
machine; only the table above describes 192.168.1.10 itself. Don't infer
which host you're on from `uname`/OS match alone — check the IP or ask.

**Open item**: a RAM upgrade was ordered but installed capacity is not
yet confirmed in this session. Verify with a real command
(`free -h` or `dmidecode --type memory`) before relying on the 3.8GB
figure above, and update this file once confirmed. Do not run
`docker compose up` against this host until the upgrade is installed and
memtested (Memtest86+, at least one full pass) — build and test images on
a dev machine until then, per TODO.md.
