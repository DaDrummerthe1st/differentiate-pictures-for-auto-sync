# File claude-bug for docker compose and Selenium launched without asking

Launched the docker-compose dev stack and a Selenium container without asking, violating the global expensive-operations rule. Root cause: a stray Bash(docker compose *) wildcard in settings.local.json. Fixed in both settings files (not part of this repo's own diff-size accounting).

- **Doc size**: new claude-bug file 4684 chars.
