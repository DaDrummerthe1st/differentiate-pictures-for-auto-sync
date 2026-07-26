# Add local static HTML/CSS/JS upload-and-share mockup

Joakim asked for the wireframe as static HTML/CSS/JS in the repo instead of a hosted Artifact — `prototypes/upload-and-share-mockup/` (index.html, style.css, script.js), no server, nothing external; ownership tiers, all three share mechanisms (including a real `navigator.share()` call for the platform-share path), and the event settings panel are all clickable with client-side-only state. Also filed and fixed a third claude-bugs report this session: `app/tests` wasn't run before four earlier commits, despite CLAUDE.md's explicit "even a docs-only one" rule — run now (58 passed), no regressions found.

- **Doc size**: prototype files 21,124 chars (`index.html` 7,666; `style.css` 7,281; `script.js` 3,918; `README.md` 412) plus the bug report, 1,847 chars.
