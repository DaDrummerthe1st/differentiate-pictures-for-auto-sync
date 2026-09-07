# Fold real .10 inventory into DEPLOY.md: live stack, taken ports, crash-looping auth

Joakim ran the read-only inventory commands on `.10` himself. Real findings replace this file's
placeholder assumptions: Docker is present, but the old photo-server stack is still live in
production (not decommissioned) with `auth` crash-looping, ports 22/25/80/443 already taken, and
a real live Postgres volume that clean-slate never applies to. `deploy.sh` still blocked on the
port/subdomain decision, now Joakim's live-production call rather than a guess.

- **Doc size**: +922 `documentation/nas/DEPLOY.md`.
