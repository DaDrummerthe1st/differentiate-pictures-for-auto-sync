# Confirm old photo-server stack retirement, mark auth crash-loop moot

Joakim ran `docker compose down` (removed caddy + all 5 other containers, verified externally by
photos.reuterborg.se failing to connect). Updated DEPLOY.md/TODO.md from "pending" to "done," noted
volumes were deliberately left intact, and marked the auth crash-loop investigation moot since the
container it belonged to no longer exists.

- **Doc size**: -20 `documentation/nas/DEPLOY.md`, -91 `documentation/nas/TODO.md`. Net -111 chars.
