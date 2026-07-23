# Server dropped to emergency mode after reboot for memtest

Status: **investigating, not fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Joakim rebooted `192.168.1.10` (`sudo reboot`) intending to hit the boot-menu key (`F12`) and select USB media to run the pending Memtest86+ pass (see [HARDWARE.md](../../../photo-server/HARDWARE.md)'s open memtest gate). The `F12` menu came up as a "choose first boot device" prompt rather than the boot-order-already-USB-first behavior he expected ("that is how I am taught"). He did **not** select USB or CD — chose the normal HDD entry. The machine then dropped into systemd emergency mode instead of booting normally. No USB/CD boot was attempted at any point this incident.

## Investigation log

1. 2026-07-23 — Incident opened. No diagnostic commands run yet; Joakim is at the physical console (screen+keyboard already connected for the memtest work) but the machine is in emergency mode, not a normal shell — SSH is almost certainly down while in this state (network stack not brought up this early in boot).
2. 2026-07-23 — Blocked: root password unknown (never set/recorded — not in HARDWARE.md, this repo has no record of it), so `sulogin`'s emergency-mode password prompt can't be satisfied. Recovery path handed to Joakim: hard power-cycle back to GRUB (unavoidable — no way out of `sulogin` without the password), edit the boot entry (`e`) to append `rw init=/bin/bash` to the `linux` line, boot that one-time edit (`Ctrl+X`/`F10`) to land in a root shell that bypasses systemd/sulogin entirely, no password needed. From there: `mount -o remount,rw /`, then `journalctl -b -1 -xb` (previous boot's log, since this rescue boot itself never ran systemd) plus `cat /etc/fstab`, `lsblk`, `blkid`. Not yet run — awaiting output.
3. 2026-07-23 — **Correction to entry 2**: a hard power-cycle was not actually necessary. The standard `sulogin` emergency-mode prompt reads `Give root password for maintenance (or press Control-D to continue):` — Ctrl+D tells systemd to proceed past the maintenance shell rather than requiring the hard reset the previous entry recommended first. Joakim recalls seeing this prompt but not its exact wording or whether Ctrl+D was pressed yet. Open question for next update: was Ctrl+D pressed, and did it (a) boot through to normal/SSH-reachable, or (b) loop back into emergency mode again — the latter would mean the failed mount/unit isn't skippable and the `init=/bin/bash` route (or a hard-reset-free equivalent, if one hasn't already happened) is still needed for diagnostics.

## Leading theory (unconfirmed)

Emergency mode is systemd's response to a boot-critical failure — most commonly a filesystem that failed to mount per `/etc/fstab` (missing device, changed device name/UUID, disk error) or a failed `fsck`. This machine just had its case open for the RAM install (4 new DIMMs seated across all 4 slots) — a plausible mechanism is a jostled SATA/power cable to the boot drive or one of the ZFS pool's `/tank` drives during that physical work, not something caused by the boot-device menu choice itself (HDD was the correct/intended choice). The BIOS boot-order prompt appearing at all (vs. silently booting USB-first as expected) is a separate, so-far-unexplained observation — possibly the RAM reseating triggered a CMOS/boot-order reset, or the "taught" USB-first expectation was never actually this board's configured order. Not yet confirmed either way.

## Next session should start with

At the physical console, from emergency mode's root shell (may prompt for the root password):
1. Read the actual failure reason: `journalctl -xb` (or check the last screenful of boot output before it dropped to emergency mode — systemd usually prints which unit/mount failed).
2. Check `systemctl --failed` for the specific failed unit.
3. If it's a mount failure, check `cat /etc/fstab` against `lsblk` / `blkid` output — look specifically for a missing or renamed device (common after any physical case work), and for whether the ZFS pool's drives are all showing up (`zpool status` if the shell allows it).
4. Do **not** attempt any destructive fix (partition/fstab edits, forced fsck) without confirming the read-only diagnosis first and getting it in front of Joakim/this file — this is the production host serving `photos.reuterborg.se`, currently down for the duration of this incident.
