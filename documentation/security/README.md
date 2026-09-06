# security/

Cross-cutting, like [tags/](../tags/README.md) and [policies/](../policies/README.md) —
not a feature folder tied to one branch. Opened 2026-07-27 after a design session
surfaced several concrete security questions (tagging/bounding-box data sensitivity,
this repo's own dev-environment risk surface, DFS-era facial-recognition security)
that didn't have a durable home; POLICY.md's existing "Privacy and safety" section
holds this project's *hard rules* (closed-by-default, moderation-supersedes-ownership),
and stays that way — this folder is where the ongoing tracking, analysis, and open
questions behind those rules actually live, so POLICY.md itself doesn't grow into a
running threat log.

**Standing principle**: security is an ongoing parallel process threaded through
every part of this project, not a one-time review gate before shipping — extends
POLICY.md's own "applies to every change, not just ones that look security-related"
line to cover the *process* of building this project, not only its shipped surface.
That includes the AI session's own dev environment: a git hook, a throwaway test
server, this development machine itself — all real attack surface, even though none
of them are the product.

| File | What's there |
| --- | --- |
| [THREATS.md](THREATS.md) | Concrete concerns identified so far, one row per concern: what it is, where it applies, current status |
| [TODO.md](TODO.md) | Open items needing real resolution — including one that needs external research, not guessing |
| [DEPENDENCIES.md](DEPENDENCIES.md) | Full-repo external-dependency inventory: license, maintenance health, CVE status per dependency, plus the CI dependency-freshness-guard coverage gap. Built 2026-09-06 after the native-app pivot. |

## Status

Opened 2026-07-27. First pass only — [THREATS.md](THREATS.md) reflects one design
session's worth of analysis, not a systematic audit. The session wrap-up checklist's
"systematic security-discovery pass" row (`pip-audit`, an OWASP ZAP baseline scan —
see [../tooling/README.md](../tooling/README.md) and
[../photo-server/TODO.md](../photo-server/TODO.md)) is the eventual mechanical
complement to this folder's design-time analysis, once `photo-server/` has a live
deployed surface to scan — neither replaces the other.
