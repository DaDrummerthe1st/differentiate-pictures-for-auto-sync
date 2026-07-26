# TODO — upload-and-share

Nothing scheduled yet — this is a design pass (see [OWNERSHIP.md](OWNERSHIP.md), [UPLOAD.md](UPLOAD.md), [SHARING.md](SHARING.md), [EVENTS.md](EVENTS.md)), not numbered TDD steps. One thing still needs resolving before numbered steps get written:

- **Legal reporting obligations** once free-for-all event upload ships — [OWNERSHIP.md](OWNERSHIP.md)'s Moderation section: a lawyer question, not resolvable by design alone.

Resolved 2026-07-26: anonymous (no-account) event upload ownership — free-for-all uploads are owned by the event's own dedicated account, not the guest and not a claimable pending record. See [EVENTS.md](EVENTS.md).

Once those are settled, this build extends the same running `server/` + `app/` codebase as [photo-server/](../photo-server/README.md) (same Postgres instance, same deployment) — its actual numbered steps most likely belong in [photo-server/TODO.md](../photo-server/TODO.md)'s phase sequence rather than a separate one here, to avoid two competing build roadmaps for one codebase. That file has a one-line pointer back to this folder in the meantime.
