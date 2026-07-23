# smartmontools and udisks2 services failed to start

Status: **investigating, not fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Found incidentally while diagnosing [2026-07-23-server-dropped-to-emergency-mode-after-reboot-for-memtest.md](2026-07-23-server-dropped-to-emergency-mode-after-reboot-for-memtest.md) on `192.168.1.10` - `systemctl --failed` shows two failed units on a boot that otherwise succeeded:
```
● smartmontools.service loaded failed failed Self Monitoring and Reporting Technology (SMART) Daemon
● udisks2.service       loaded failed failed Disk Manager
```
Neither appears to block the ZFS pool (`tank` is `ONLINE`, no data errors) or the production `docker compose` stack (confirmed up and serving).

## Investigation log

1. 2026-07-23 — `journalctl -p err -b` shows, for `smartmontools.service`: `smartd` logging a generic firmware-bug caution for `/dev/sdb` and `/dev/sdd` ("Using smartmontools or hdparm with this drive may result in data loss due to a firmware bug... THIS DRIVE MAY OR MAY NOT BE AFFECTED") before the service fails to start at `12:20:48`. This looks like `smartd`'s standard canned warning for certain older Seagate/Samsung-era drives, not necessarily an active fault on these specific disks - not yet confirmed either way. `udisks2.service`'s failure (`12:21:02`) has no corresponding error-level log line captured in what was pulled (`journalctl -p err -b | tail -100` may have missed earlier context, or the actual failure reason logged at a lower priority) - reason unknown.
2. Timing note: both failures happened ~25-26 minutes into a 25-minute-uptime boot that also involved reconnecting the ZFS-pool dock's SATA cable and fixing a BIOS boot-priority issue - plausible these are downstream of the same session's drive/boot churn (e.g. a service timing out while disks were still settling), but not yet confirmed as related to that incident rather than pre-existing.

## Leading theory (unconfirmed)

Not yet distinguished between: (a) pre-existing, unrelated to tonight's incident, just never previously surfaced under `systemctl --failed`; (b) a side effect of the same boot's drive reconfiguration (extra/reordered drives confusing `udisks2`'s or `smartd`'s own device enumeration at startup).

## Next session should start with

1. `systemctl status smartmontools.service udisks2.service --no-pager -l` for full status/error text on each.
2. `journalctl -u smartmontools.service -u udisks2.service -b --no-pager` for their specific logs (broader than the `-p err` filter used when this was first found, which may have missed relevant non-error-priority lines).
3. Try `sudo systemctl restart smartmontools.service udisks2.service` and see if they come up clean on a retry now that the disk situation has settled - if so, this may just have been a one-time startup-ordering race during tonight's churn, not a persistent config problem.
