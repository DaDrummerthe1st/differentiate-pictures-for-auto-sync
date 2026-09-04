# Correct CardDAV auth: App Password, not a registered OAuth client

Joakim caught a mistake in the design pass just committed: he never sees an OAuth consent screen
using Thunderbird's Google CardDAV sync, so Thunderbird can't be a Google-approved OAuth app the way
the earlier text assumed. Web-searched Google's own support/blog pages to check rather than guess:
confirmed Google keeps an **App Password** (a self-generated, revocable credential for non-OAuth
apps, requiring 2-Step Verification) open as the supported CardDAV fallback — no registered/reviewed
OAuth client needed at all, same shape as iCloud's app-specific password. Corrected GLOSSARY.md,
IDENTITY_MATCHING.md, THREATS.md row 17, and tags/TODO.md's Contacts-import item accordingly; the
guided-session next step is now "generate an App Password," not "register an OAuth client."

- **Doc size**: GLOSSARY.md +931, curation/IDENTITY_MATCHING.md +611, security/THREATS.md +400,
  tags/TODO.md +145.
