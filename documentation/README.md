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
| [file-integrity/](file-integrity/README.md) | Content-sniffed file-type verification apparatus |
| [bugs/](bugs/README.md) | Bug/incident reports and AI-session process-lapse tracking |
| [changelog/](changelog/README.md) | One-file-per-entry changelog; old `CHANGELOG.md` frozen as [CHANGELOG_ARCHIVE.md](../CHANGELOG_ARCHIVE.md) |
| [tooling/](tooling/README.md) | Project-wide dev utilities (`tools/`) — not topic-specific |

**Requested, not yet built (2026-07-29)**: a `GLOSSARY.md` — human-readable, plain-language definitions of every technical term this project's design docs use (DHT, IPFS, PoW/PoS/proof-of-useful-work, the ownership tiers, EDPB, GDPR's household exemption, biometric/special-category data, etc.), written for a non-specialist reader. Requested explicitly because the inline "for dummies" explanations given in-conversation during the 2026-07-28/29 tag/sharing/security design session didn't fully land, especially the EDPB/GDPR facial-recognition finding (`security/TODO.md` item 6) — a durable, well-organized glossary is meant to replace re-deriving these explanations ad hoc each time. Once built: "extract and delete all similar tellings from other places" — i.e., where a design doc currently explains a term inline as an aside, point to the glossary instead of re-explaining, keeping the term's actual design usage in its home doc and the plain-language explanation in one place. Not started this session — top priority for whichever session picks this up next.
