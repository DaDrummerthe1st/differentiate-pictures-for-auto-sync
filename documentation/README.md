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
