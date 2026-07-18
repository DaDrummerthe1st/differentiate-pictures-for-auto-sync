# EdgeRouter SSH login fails for JokeHim despite working web UI credentials

Status: **investigating, not fixed**. Keep this file as the full
chronological trail as more is learned - don't overwrite conclusions.

Split out 2026-07-18 from
`2026-07-18-photos-reuterborg-se-unreachable.md` - found while
troubleshooting that outage, but this is a distinct problem (router
account access) from the server's `NO-CARRIER` issue and gets its own
file per CLAUDE.md's one-bug-one-file rule.

## Symptom

`ssh JokeHim@192.168.1.1` prompts for a password and rejects it
(`Permission denied, please try again.`), even though the same
username/password logs into the router's web UI successfully (Firefox
saved credentials, confirmed working 2026-07-18).

Joakim confirmed SSH access to this router worked as recently as
yesterday (2026-07-17, same day the server's own SSH last worked - see
the outage report). This is a regression since then, not a
never-worked account.

## Investigation log

1. First attempt used username `JokeHime` (typo) - correctly rejected
   with `Permission denied`. Corrected to `JokeHim` (verified against
   the Firefox-saved credential) - **still rejected** with the same
   password that works on the web UI.
2. SSH's own banner/handshake was checked before the credential
   failure: EdgeOS's normal login banner displayed immediately, with no
   host-key-changed warning. This rules out a router reset/reflash as
   the cause (a reset would present a fresh, unrecognized host key) -
   the router's identity is the same one previously trusted.
3. No fallback account to test with: the factory-default admin account
   was deliberately removed previously for security (Joakim's call,
   correct one - just means there's no second account available to
   isolate "this specific account" vs. "SSH service generally" right
   now).
4. Deprioritized relative to the concurrent server outage - GUI access
   is sufficient for that investigation's needs, so this wasn't chased
   further same-session.

## Leading theory (unconfirmed)

Credentials are correct (proven via the web UI) and the SSH service
itself is up and presenting the right host identity - so this points at
something account- or service-config-specific to SSH rather than a
router-wide problem: e.g. a permission/level setting on the `JokeHim`
account that grants GUI access but not shell/SSH access, or a
config change (intentional or accidental) to `service ssh` restricting
which accounts may authenticate that way. Not yet confirmed - needs
looking at from a session that has either working SSH under a different
account, or the GUI's own user-management view of `JokeHim`'s
configured permission level.

## Next session should start with

1. In the web UI, find the user-management / system-users view and
   check what permission level `JokeHim` is configured with - EdgeOS
   distinguishes an "operator" level (typically GUI monitoring, no
   config/shell) from "admin" (full access including SSH). If it's
   `operator`, that alone explains this without any bug at all.
2. If the level is already `admin`, check `service ssh` config (GUI or,
   once any account can get a shell, `show configuration | grep -A5 ssh`)
   for anything scoping which users/groups may authenticate over SSH.
3. Not urgent - this doesn't block the outage investigation in
   `2026-07-18-photos-reuterborg-se-unreachable.md`, which only needed
   GUI access.
