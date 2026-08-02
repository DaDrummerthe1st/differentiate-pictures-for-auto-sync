# documentation/

Project documentation, organized by topic. Structure/maintenance rules: [CLAUDE.md](../CLAUDE.md). Long-term direction across all topics: [VISION.md](VISION.md).

| Folder | What's there |
| --- | --- |
| [policies/](policies/README.md) | Hard, project-wide constraints, and cross-cutting topics like authentication |
| [security/](security/README.md) | Cross-cutting: ongoing threat/concern tracking, open security questions — not the hard rules themselves (those stay in policies/) |
| [tags/](tags/README.md) | Cross-cutting: the tag taxonomy — categories, schema, sharing/privacy model — referenced by every topic below, not owned by one |
| [photo-server/](photo-server/README.md) | Current work: multi-user web server — browse, search, tag, download |
| [upload-and-share/](upload-and-share/README.md) | Design work: per-user upload, ownership/sharing terms, event/party mode (`upload-and-share` branch) |
| [gui/](gui/README.md) | The photo-server GUI's first working version (`mamma-photo-viewer` branch) |
| [picture-handling/](picture-handling/README.md) | Superseded single-machine sorting tool — resolved, moved to photo-server/ |
| [distributed-sync/](distributed-sync/README.md) | Future work: multi-device sync, distributed storage/compute |
| [income/](income/README.md) | Business/monetization ideas — rollout phases, revenue ideas, not committed design |
| [file-integrity/](file-integrity/README.md) | Content-sniffed file-type verification apparatus |
| [bugs/](bugs/README.md) | Bug/incident reports and AI-session process-lapse tracking |
| [changelog/](changelog/README.md) | One-file-per-entry changelog; old `CHANGELOG.md` frozen as [CHANGELOG_ARCHIVE.md](../CHANGELOG_ARCHIVE.md) |
| [tooling/](tooling/README.md) | Project-wide dev utilities (`tools/`) — not topic-specific |

[GLOSSARY.md](GLOSSARY.md) — plain-language definitions of every technical/business term this project's docs use. Built 2026-07-29; append to it (per [CLAUDE.md](../CLAUDE.md)'s non-negotiable rule) rather than re-explaining a term inline in a design doc.

## Layout conventions

- Every subfolder (root included) has its own `README.md`: what the folder is for, plus an index of its children only if that adds something a reader wouldn't already get from each child's own opening line.
- [policies/POLICY.md](policies/POLICY.md) (not `README.md` — a deliberate naming exception so "hard rules live here" is unmistakable) holds genuinely project-wide hard constraints; nothing project-wide gets duplicated outside it.
- **Topic folders** (a subject with its own ongoing open work) get a mandatory `TODO.md` — open/deferred items, or "nothing planned right now" if empty; never delete it for being empty, the point is proving absence was checked. Pure reference folders (like `policies/`) don't need one.
- Root `README.md` is the public-facing GitHub landing page (short pitch + pointer here); [CLAUDE.md](../CLAUDE.md) is the working agreement for whoever — human or AI — is doing the work.
- **No hard-wrapping prose to a fixed column width** — one paragraph/list-item/blockquote per line, let the viewer soft-wrap. **Why:** measured against the real corpus 2026-07-19 — hard-wrap cost more characters than it saved; full measurement in `CHANGELOG_ARCHIVE.md`'s 2026-07-19T04:39:12+00:00 entry.
- **All documentation lives under `documentation/`** — code directories (`server/`, `tools/*/`) get at most a one-line stub `README.md` pointing here, never real content. Decided 2026-07-16 after `server/README.md` and two `tools/*/README.md`s drifted into real content — moved and replaced with stubs.

## Keeping docs current

When a change affects schema, API surface, or architecture, update the relevant doc in the same pass — don't let docs drift from what the code does. (Known existing drift: see [documentation/picture-handling/TODO.md](picture-handling/TODO.md) for the MySQL-vs-PostgreSQL mismatch.)
