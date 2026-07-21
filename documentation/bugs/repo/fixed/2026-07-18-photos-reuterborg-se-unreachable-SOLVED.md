# photos.reuterborg.se unreachable

Status: **solved 2026-07-18**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Found 2026-07-18, Joakim reported the app broken (screenshot: album grid showing "0 av 16 album visade", most thumbnails not rendering). From the dev machine (same LAN as the server, `192.168.1.0/24`):

```
$ curl https://photos.reuterborg.se/health
curl: (7) Failed to connect to photos.reuterborg.se port 443 after 3063 ms: Couldn't connect to server
```

## Investigation log

1. DNS: `photos.reuterborg.se` resolves to `82.183.62.213` - correct, confirmed below.
2. Public IP check: curled two independent external services (`ifconfig.me`, `api.ipify.org`) from the dev machine, which is on the same home network as the server. Both returned `82.183.62.213` - **identical to the DNS A record**. The public IP has not changed; DNS is not the problem.
3. LAN-level check of the server itself (`192.168.1.10`): `ping` gets 100% packet loss, `ip neigh show 192.168.1.10` reports `INCOMPLETE` (the router got no ARP reply for that IP), and a raw TCP attempt on ports 22/80/443 all return "No route to host". This means the machine isn't answering at the network layer at all - not an app/container-level problem.
4. Joakim confirmed (2026-07-18): he is physically at the machine, it's powered on, ethernet cable is seated, and he SSH'd into it successfully yesterday (2026-07-17).
5. Ran a full subnet scan (`nmap -sn 192.168.1.0/24`) in case the server came back up under a different DHCP-assigned IP (Joakim noted `192.168.1.10` is *supposed* to be a static/reserved address, worth confirming rather than assuming). Found 6 hosts up: `.1` (gateway), `.2`, `.70`, `.107`/`.108` (the dev machine itself, wifi+ethernet), `.109`. **No `.10`.**
6. Probed `.2`, `.70`, `.109` for open 22/443: `.2` and `.70` both have 22 open but not 443 (existing unrelated LAN devices, not the photo server); `.109` has neither open. None of the discovered hosts looks like the photo-server stack currently serving anything on 443.
7. Joakim got physical bash control on the server itself (SSH to it still doesn't work - separate from this investigation, not yet understood). **Confirmed directly on the box: no IP assigned at all.** `ip a` shows `NO-CARRIER` on the ethernet interface - the NIC detects no signal on the cable, despite the cable being physically seated at the server end and its port LEDs appearing to flash (ambiguous signal - flashing doesn't always mean a negotiated link; not treated as conflicting evidence against `NO-CARRIER`, which is the authoritative kernel-level read).
8. `sudo dhclient -v enp2s0` was tried and doesn't exist on this box (Ubuntu 24.04 uses `netplan`/`systemd-networkd`, not `isc-dhcp-client`) - moot regardless, since `NO-CARRIER` means no DHCP request could go out over that link even with the right tool.
9. Checked the EdgeRouter X (`192.168.1.1`) for its side of the same port. Web UI login (Firefox-saved credentials, account `JokeHim`) works. SSH login failed first on a username typo (`JokeHime` vs the correct `JokeHim`); after fixing that, SSH *still* fails to authenticate with the same credentials that work on the web UI. Joakim confirmed router SSH worked as recently as yesterday (2026-07-17, same day the server's own SSH last worked) - a regression since then, not a never-worked account. No fallback account to isolate with (the factory-default admin account was deliberately removed previously, for security). Using the working GUI instead of chasing this further mid-outage.
10. SSH's banner/handshake was checked before the credential failure: EdgeOS's normal login banner displayed immediately, with no host-key-changed warning - the router's identity is the same one previously trusted, so this specific evidence doesn't support a router reset/reflash as a shared cause. Not fully ruled out as related to this outage either way, though (e.g. a permission/config change scoped to SSH specifically, rather than a full reset, could still share a cause with the network-layer symptom without showing up in the host key) - keeping both threads in this one file rather than assuming they're unrelated.

11. **Topology correction**: the server is not plugged directly into the EdgeRouter - it connects to a switch, which connects to the router. `HARDWARE.md` doesn't currently document this switch at all. This means the EdgeRouter's own port-status view (log entry 9's plan) only reflects the switch-to-router link, not the server-to-switch link where `NO-CARRIER` was actually observed - it can't diagnose this specific symptom. Identified as a Linksys LGS1xx-series switch (unmanaged - no web UI, no software port diagnostics available at all on it).
12. **Root cause found and fixed**: the switch had been powered continuously for "probably a couple of years" with no reboot. Joakim power-cycled it (pulling its power adapter - the only kind of restart an unmanaged switch has). The server's NIC picked up `NO-CARRIER` -> live link immediately once the switch finished rebooting. A stuck port state on a switch that had never been restarted in years is the confirmed cause - not a bad cable, not a dead NIC port, not the router.

## Leading theory (confirmed)

An aging unmanaged switch, never rebooted in years, got into a stuck port state that produced `NO-CARRIER` on the server's side of that link. A power cycle of the switch resolved it immediately - no cable, NIC, or router hardware fault. `HARDWARE.md` should be updated to document this switch's existence in the topology (not done yet - open below).

## Next session should start with

1. **Documentation gap**: `HARDWARE.md` doesn't mention this switch (make/model: Linksys LGS1xx-series, unmanaged) at all in the server's network topology - add it, including this incident as the reason a periodic preventative reboot might be worth considering for an unmanaged switch with years of continuous uptime.
2. Separately, still open and unrelated to this outage (confirmed via the SSH banner showing no router host-key change): `JokeHim` can log into the router's web UI but not SSH with the same credentials, a regression since yesterday. In the web UI's user-management view, check what permission level `JokeHim` is configured with - EdgeOS distinguishes an "operator" level (GUI monitoring only) from "admin" (full access including SSH); if it's `operator`, that alone would explain this. If already `admin`, check `service ssh` config for anything scoping which accounts may authenticate that way.
3. A second, distinct issue was found immediately after this one resolved (same power event, different mechanism - Redis losing session state on restart) - see `2026-07-18-redis-has-no-persistent-volume-every-restart-wipes-active-sessions.md`.
