# TODO — upload-and-share

Nothing scheduled yet — this is a design pass (see [OWNERSHIP.md](OWNERSHIP.md), [UPLOAD.md](UPLOAD.md), [SHARING.md](SHARING.md), [EVENTS.md](EVENTS.md)), not numbered TDD steps. Two things need explicit confirmation from Joakim before numbered steps get written:

- **Anonymous (no-account) event upload ownership** — [EVENTS.md](EVENTS.md)'s Open questions: proposed a claimable pending-owner record, not yet confirmed.
- **Legal reporting obligations** once free-for-all event upload ships — [OWNERSHIP.md](OWNERSHIP.md)'s Moderation section: a lawyer question, not resolvable by design alone.

Once those are settled, this build extends the same running `server/` + `app/` codebase as [photo-server/](../photo-server/README.md) (same Postgres instance, same deployment) — its actual numbered steps most likely belong in [photo-server/TODO.md](../photo-server/TODO.md)'s phase sequence rather than a separate one here, to avoid two competing build roadmaps for one codebase. That file has a one-line pointer back to this folder in the meantime.
