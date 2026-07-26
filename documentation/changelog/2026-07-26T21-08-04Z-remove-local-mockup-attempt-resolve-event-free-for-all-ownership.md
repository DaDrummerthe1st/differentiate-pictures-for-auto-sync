# Remove local mockup attempt, resolve event free-for-all ownership

Joakim's call: the local static HTML/CSS/JS attempt (`prototypes/upload-and-share-mockup/`) just re-rendered the written docs as styled cards rather than being a real clickable prototype with fake data and state transitions — deleted rather than iterated on further. Also resolves a real open design question from earlier this session: free-for-all event uploads are owned by the event's own dedicated account, never the anonymous guest and never a claimable pending record (that mechanism stays for the unrelated email-invite path) — updates EVENTS.md, the `events` schema entry, and closes out one of upload-and-share/TODO.md's two blockers, leaving only the legal-reporting-obligations question before build steps can be written.

- **Doc size**: removed `prototypes/upload-and-share-mockup/`, 21,124 chars. Edited docs (README.md, EVENTS.md, TODO.md, DATA_DICTIONARY.md): 16,352 → 16,797 chars (+445).
