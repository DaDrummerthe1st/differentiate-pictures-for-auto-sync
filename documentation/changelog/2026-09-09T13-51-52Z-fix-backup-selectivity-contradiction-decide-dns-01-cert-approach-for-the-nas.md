# Fix backup-selectivity contradiction, decide DNS-01 cert approach for the NAS

`SYNC_CONTRACT.md` claimed every photo original eventually lands on the NAS regardless of the
user's choices, directly contradicting its own "user decides, always" ground rule two paragraphs
above — fixed to fully selective backup, `explicit-backup` renamed `preset-full-backup` to match.
Self-review also caught and reconciled a device-revocation inconsistency against `DATA_MODEL.md`
(soft `revoked_at`, not row deletion). Separately, corrected `ARCHITECTURE.md`'s assumption that
staying LAN/VPN-only meant avoiding Let's Encrypt entirely — DNS-01 challenges need no open port,
so a real trusted cert (POLICY.md's one named closed-by-default exception) works fine here and beats
self-signed/local-CA for a phone that syncs from arbitrary networks (home Wi-Fi or cellular, both via
WireGuard). Decided for `.10`: reuse `photos.reuterborg.se`, ACME runs on-box. Flagged, not designed:
the cert-issuance-at-scale question for a real multi-NAS product (CNAME-delegated per-user
subdomains, Tailscale/Synology precedent researched) in `TODO.md`.

- **Doc size**: +2650 `documentation/GLOSSARY.md`, +2201 `documentation/nas/ARCHITECTURE.md`, +279 `documentation/nas/DATA_MODEL.md`, +540 `documentation/nas/DEPLOY.md`, +2161 `documentation/nas/SYNC_CONTRACT.md`, +4035 `documentation/nas/TODO.md`.
