# No log persistence guarantee across the stack

Status: **not attempted**.

## Requirement

Joakim, 2026-07-17, explicit: "ALL logs need to be persistent, even docker's."

## Current state

Today's `docker-compose.prod.yml` doesn't configure a logging driver at all for any of the 5 services, so they use Docker's default (`json-file`, written to the host under `/var/lib/docker/containers/...`) — this *does* survive a container restart, but is lost if a container is recreated (e.g. every `up -d --build`, which happened several times during today's deploy) and isn't rotated/bounded by anything in this repo's own config.

Not affected: the app's own `audit_log`/`analytics.db` already persist correctly via named volumes (confirmed in DEPLOYMENT.md's verify step). This is specifically about Docker's own container logs (stdout/stderr), not application data.

## Real fix, not attempted today

An explicit logging driver + rotation policy (e.g. `json-file` with `max-size`/`max-file`, or a bind-mounted log directory) added per-service in `docker-compose.prod.yml`, covering all 5 containers. Needs testing (does a real restart actually preserve them under the new config?) before trusting it.
