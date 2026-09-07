# Decide LAN+WireGuard-only exposure for the NAS, retire the old public photo-server

Joakim confirmed photos.reuterborg.se's stack is obsolete and can be retired, and floated
LAN-only reachability for the NAS PWA. Adopted: no public hostname/port at all — LAN direct,
off-LAN via the existing WireGuard tunnel, no Let's Encrypt cert needed. Resolves the earlier
port-collision blocker outright rather than picking a port on the live Caddy config.

- **Doc size**: +1098 `documentation/nas/ARCHITECTURE.md`, +1172 `documentation/nas/DEPLOY.md`, +417 `documentation/nas/TODO.md`. Total +2687 chars.
