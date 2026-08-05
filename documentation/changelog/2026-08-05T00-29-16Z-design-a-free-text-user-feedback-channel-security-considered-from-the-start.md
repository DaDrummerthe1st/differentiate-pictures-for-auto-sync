# Design a free-text user feedback channel, security considered from the start

Joakim asked for a free-text feedback mechanism, security thought through explicitly rather than as an afterthought — in service of a new standing VISION.md principle: the system should help the user in any way it can, not just via structured tagging/sharing.

Design sketch in photo-server/DEFERRED.md (not built): a `feedback` table (`user_id, text, status` for admin triage), authenticated-only submission (no anonymous path needed at 2-3-account scale), length-capped and rate-limited the same way `/login` already is (`slowapi`), escaped-on-render like tag text (never interpreted HTML/markdown), visible only to the admin account, no third-party helpdesk SaaS. Flagged honestly rather than assumed solved: there's no admin GUI at all today, so a feedback-*viewing* surface has the same unbuilt prerequisite the CVE-monitoring item already named; and the threat model changes once Pillar 3's less-verified upload modes let non-household people submit feedback too.

Tracked as a new threat row (THREATS.md #13) since feedback text is rendered for a different, higher-privilege account (the admin) than its author — a stored-XSS hit here is more valuable to an attacker than the existing peer-to-peer tag-text case (#3).

GLOSSARY.md gets XSS/stored-XSS, CSRF, and rate-limiting entries.

- **Doc size**: +5,122 chars (net, across VISION.md, photo-server/DEFERRED.md, security/THREATS.md, GLOSSARY.md; Unicode codepoints, per DOC_METRICS.md methodology).
