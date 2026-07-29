# TODO — upload-and-share

Nothing scheduled yet — this is a design pass (see [OWNERSHIP.md](OWNERSHIP.md), [UPLOAD.md](UPLOAD.md), [SHARING.md](SHARING.md), [EVENTS.md](EVENTS.md)), not numbered TDD steps. One thing still needs resolving before numbered steps get written:

- **Legal reporting obligations** once free-for-all event upload ships — [OWNERSHIP.md](OWNERSHIP.md)'s Moderation section: a lawyer question, not resolvable by design alone.
- **Blocked-sender feedback**: silent failure vs. an explicit "you're blocked" message when a blocked user attempts to share — [ABUSE_MITIGATION.md](ABUSE_MITIGATION.md)'s Blocking section, real anti-retaliation UX call, not made yet.
- **Receive-time nudity/NCII classifier**, gating condition for ever shipping the `open` sharing-consent mode — [ABUSE_MITIGATION.md](ABUSE_MITIGATION.md), ties to [../tags/TODO.md](../tags/TODO.md)'s nudity auto-detection item; DPFAS-phase, not started.
- **V1 sharing without an account — raised 2026-07-29, not resolved.** All three [SHARING.md](SHARING.md) mechanisms eventually assume the recipient gets (or already has) a DPFAS account (the email-invite path resolves via signup; the platform/username paths need one directly). Joakim's question: should V1 also support a genuinely account-free share — a plain download link/file, like sending a copy from your own hard drive — for the simplest "just get this photo to someone" case, rather than *only* the pending-signup flow? Not designed; needs a real decision before V1's sharing UX is spec'd.
- **Event-space rental income idea moved to [../income/TODO.md](../income/TODO.md), 2026-07-29** — business/monetization content, not this file's own technical scope.

Resolved 2026-07-26: anonymous (no-account) event upload ownership — free-for-all uploads are owned by the event's own dedicated account, not the guest and not a claimable pending record. See [EVENTS.md](EVENTS.md).

Once those are settled, this build extends the same running `server/` + `app/` codebase as [photo-server/](../photo-server/README.md) (same Postgres instance, same deployment) — its actual numbered steps most likely belong in [photo-server/TODO.md](../photo-server/TODO.md)'s phase sequence rather than a separate one here, to avoid two competing build roadmaps for one codebase. That file has a one-line pointer back to this folder in the meantime.
