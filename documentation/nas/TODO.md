# nas/ TODO

## Designed this session (2026-09-07), nothing built beyond scaffolding

- Architecture, tech stack, storage layout, detector porting, DFS/marketplace extension seam — [ARCHITECTURE.md](ARCHITECTURE.md).
- Postgres schema new to the NAS (`photos`, `devices`, `sync_queue`, `detector_runs`, `embeddings`) — [DATA_MODEL.md](DATA_MODEL.md).
- Phone↔NAS sync contract draft (pairing, endpoints, user-controlled priority) — [SYNC_CONTRACT.md](SYNC_CONTRACT.md). **Needs the mobile session's review before either side implements against it.**
- Deploy target and process shape — [DEPLOY.md](DEPLOY.md). `deploy.sh` itself blocked on Joakim's inventory pass of `.10`.

## Open, blocking further work

- **Inventory pass on `.10` — done 2026-09-07**, see [DEPLOY.md](DEPLOY.md). `deploy.sh` itself still not written — the remaining blocker is the port/cert choice (self-signed vs. local CA), not missing inventory data anymore.
- **Pilot-usage-learning vs. no-telemetry tension, flagged not resolved** — see [ARCHITECTURE.md](ARCHITECTURE.md)'s Open tension section and [../policies/POLICY.md](../policies/POLICY.md)'s Open questions. Needs Joakim's explicit call before any usage-analytics mechanism is designed.
- **Coordinate `SYNC_CONTRACT.md` with the mobile session** — the pairing flow and queue-polling model both assume specific phone-side behavior (Keystore-held device key, a background sync worker that polls `/sync/queue`) that session hasn't seen or agreed to yet. **2026-09-07**: Joakim will relay this himself rather than this session messaging the peer directly.

- **Phone's off-LAN sync path — direction confirmed 2026-09-07, not designed in detail**: WireGuard is the answer for the phone too, same as for a remote PWA browser — a second WireGuard peer alongside the existing Lenovo-workstation one, per [NETWORK.md](NETWORK.md)'s topology diagram. Not designed beyond that: peer provisioning at pairing time, how the phone's WireGuard client is configured/stored, whether it piggybacks on [SYNC_CONTRACT.md](SYNC_CONTRACT.md)'s device-pairing flow or is separate. Needs the mobile session's input, since the phone-side half is its territory.

## Security follow-up on `.10`, raised 2026-09-07 — unrelated to NAS design, surfaced by the inventory pass

- **`auth` container crash-looping — moot**, the whole stack it belonged to is retired (see below). Root cause never diagnosed; not worth chasing for a container that no longer exists, unless the login-history audit below turns up a reason to suspect it was symptom rather than ordinary bug.
- **Security/access audit requested** — who's logged in, login history, failed logins, full listening-port picture, and specifically whether **"buzzkit"** (one of Joakim's other, unrelated projects) is somehow running on `.10` — he noticed it "active and operational" while pasting inventory output, unconfirmed whether that was actually observed on `.10` itself or elsewhere. Diagnostic commands handed to Joakim; **results not yet seen by this session** — pick this up first thing next session if Joakim has output by then.
- **Old `photos.reuterborg.se` stack — retired 2026-09-07**, done. See [DEPLOY.md](DEPLOY.md). Verified externally (browser connection failure) and via `docker ps -a`/`docker compose down` output — `caddy` included, not just backend services. Volumes deliberately left intact (real data).
- **Port hardening, still open**: whether `.10`'s SSH (`22`) is reachable from the WAN depends on the EdgeRouter's own port-forward table (a separate device, not inspectable from `.10`'s own commands) — the hardware repo's network doc (last verified 2026-08-07) says only `80`/`443` were forwarded, worth Joakim reconfirming live on the router directly, especially now that `80`/`443` no longer need forwarding at all either.

## Session TODO, opened 2026-09-09 — tracked here since TodoWrite is currently unavailable

Joakim asked for this backlog tracked as a running list, starting execution this session. Plain markdown, not TodoWrite, for the same reason [../mobile/TODO.md](../mobile/TODO.md)'s 2026-09-09 snapshot gives (see its own note) — the tool is currently unavailable, tracked separately as a claude-bug in the `claudefiles` repo.

- [x] **`SYNC_CONTRACT.md` review** — done this session (2026-09-09), see that file's new "Self-review pass" note under Status: fixed the backup-selectivity contradiction and a devices-row-deletion vs. `revoked_at` inconsistency; flagged two remaining open questions (pairing-code lifecycle, queue-request cancellation) for the mobile session.
- [ ] **Phone's off-LAN path (WireGuard peer for the phone)** — direction confirmed 2026-09-07 (a second WireGuard peer, same as the existing Lenovo-workstation one), not designed in detail. Blocked on the mobile session's input (Keystore-held WireGuard config storage, whether it piggybacks on the device-pairing flow above or is separate) — this session can't design the phone-side half unilaterally.
- [ ] **`.10` security/access audit** — requested during the 2026-09-07 inventory pass (login history, failed logins, full listening-port picture, and specifically whether "buzzkit," one of Joakim's unrelated other projects, is actually running on `.10`). Diagnostic commands already handed to Joakim; results not yet seen by this session. Blocked on Joakim running those commands himself, per the hard rule below.
- [x] **Port/cert choice for `nas/deploy.sh`** — **decided 2026-09-09**: Let's Encrypt via DNS-01 challenge (see [ARCHITECTURE.md](ARCHITECTURE.md)), not self-signed/local-CA — needs no open port, stays consistent with LAN+WireGuard-only exposure, and is already POLICY.md's one named exception to closed-by-default. Subdomain: reuse `photos.reuterborg.se`. Automation: runs on `.10` itself (acme.sh/certbot, DNS-01 plugin), Joakim's to set up. Actual port number still open but no longer blocking design — pick anything free at build time.
- [ ] **Detector porting (code) and PWA screens to wireframe level** — [ARCHITECTURE.md](ARCHITECTURE.md) says where detector code will live but none exists yet; [UX_FLOWS.md](UX_FLOWS.md) is vision-level only. Largest remaining item, not started.
- **Standing rule, not a task**: this session never touches `.10` directly (no SSH/ping/curl) — every command above that needs to run against the real box is written for Joakim to copy and run himself, per [DEPLOY.md](DEPLOY.md).

## Not designed at all yet

- Actual detector porting (code) — [ARCHITECTURE.md](ARCHITECTURE.md)'s Detector porting section says where NAS-side inference code will live and what it writes ([DATA_MODEL.md](DATA_MODEL.md)'s `detector_runs`), but no code exists; model choice itself stays [../curation/DETECTORS.md](../curation/DETECTORS.md)'s call, not redecided here.
- The NAS PWA's screens down to component/wireframe level — [UX_FLOWS.md](UX_FLOWS.md) sketches the screens vision-level, same bar as [../tags/UX_FLOWS.md](../tags/UX_FLOWS.md); not build-ready.
- Multi-NAS (V2 rollout, each user her own box) — explicitly out of scope; this pass is one box (`.10`) only.
  - **Cert issuance at scale, raised 2026-09-09, flagged not designed**: `.10`'s cert scheme (reuse `photos.reuterborg.se`, ACME on-box) is a one-user solution that doesn't generalize — a real multi-NAS product can't have every user's box requesting a cert for the same shared personal domain. Real precedent exists to research when V2 actually starts: Tailscale's MagicDNS/HTTPS issues each device its own subdomain under a company-controlled domain, with the coordination server completing the Let's Encrypt DNS-01 exchange centrally and shipping the cert down to the device (the device itself never holds DNS-provider API credentials); Synology QuickConnect instead relays traffic through a company-run endpoint whose cert is what the browser actually validates. The DNS-01-specific mechanism both lean on is **CNAME delegation** — a user's `_acme-challenge` subdomain record is a CNAME pointing at a project-controlled zone, so the project's automation can complete challenges without ever holding a customer's real domain credentials. Given [distributed-sync/README.md](../distributed-sync/README.md)'s "no single point of dependency on a third-party quota" principle, **on-box ACME automation with per-user CNAME-delegated subdomains** (not a company-run relay every user's access depends on) is the better fit for this project specifically — flagged as the leading direction, not designed or built.
- DFS / bought-disk-space integration — deliberately not designed, per [ARCHITECTURE.md](ARCHITECTURE.md)'s extension-seam note.

## Status

Opened 2026-09-07. By session close: architecture/schema/UX/network design done, `.10` inventory done, old public stack retired and verified down, security/access audit commands handed off but results not yet seen. Design-only throughout — no code written.
