# Used private AI memory for project content despite the self-sufficiency rule

See [README.md](../README.md) for what belongs here.

## What happened

`WORKFLOW.md`'s Self-sufficiency section states plainly: "Decision history, status, future plans, and reusable lessons belong in this repo... never only in a private/local AI memory store." Despite this, the harness's private auto-memory store for this project (`~/.claude/projects/-home-joakim-code-project-differentiate-pictures-for-auto-sync/memory/`) accumulated 24 entries across many sessions (2026-08-02 through 2026-09-07) — feedback lessons, project status notes, a user-preference note — read and cited by this session at the start of every turn, exactly the "private/local AI memory store" the rule names.

Joakim caught this by recalling a similar correction from around July, on a different project (`buzzkit`) — confirmed real: `buzzkit`'s own memory has a note dated 2026-07-09 saying that project "keeps no private AI memory by design... everything durable lives in the repo itself." Neither that July correction nor this project's own explicit WORKFLOW.md rule (which predates most of the 24 entries) had actually stopped the behavior — the rule was documented but never mechanically enforced, so it kept getting worked around/missed session to session.

## Why it happened

The harness's auto-memory system is presented generically (in the system prompt, on every session) as a feature to actively build up over time — nothing in that generic framing checks a given project's own CLAUDE.md/WORKFLOW.md for an opt-out before writing. This project's self-sufficiency rule is a project-level override of that generic default, and honoring it required *remembering to check for and apply* the override every single session — exactly the kind of judgment-dependent, not-mechanically-checkable failure mode this project has already named elsewhere ([[user_wants_honest_capability_limits]]-style: some fixes can get a hard gate, others can't without a real mechanism to point at). A restated rule in a doc is not a mechanism.

## What changed

- Added `"autoMemoryEnabled": false` to this project's checked-in `.claude/settings.json` — a real, mechanical block (the harness's own documented setting for exactly this) rather than a rule a future session has to remember to apply. This is the difference from the July `buzzkit` correction, which was documentation-only and evidently didn't hold here.
- Migrated durable content from the 24 memory entries into the repo, per the recommended-and-approved plan (migrate then clear), rather than just discarding them:
  - `WORKFLOW.md` gained a new "Debugging discipline" section (root-cause tracing, no speculative fixes, permission-prompt config-first diagnosis, logs-not-screenshots for GUI checks) and a "concurrent sessions sharing one working directory" rule under "Other standing rules" (which also let `documentation/bugs/repo/under_process/2026-09-04-concurrent-sessions-...md` finally close — it had been sitting on "add this to WORKFLOW.md, that's the fix" since 2026-09-04).
  - `POLICY.md`'s Deployment and system access section gained an explicit "no SSH/read-only reach into real infra either, not just deploys" bullet plus a pointer to the separate `hardware` repo.
  - `documentation/mobile/TODO.md` gained a dev-conventions bullet (emulator-only by default, logs-not-screenshots).
  - `documentation/README.md`'s Layout conventions gained the rename/repoint-pass rule (don't rewrite historical narrative to a file's new name).
  - Several entries turned out to already be fully covered in-repo (glossary routine, TDD test-first, explain-in-chat, the trailing-questions/AskUserQuestion rule, the permission-prompt-diagnosis incident itself) — nothing further needed for those.
  - A few entries were genuinely global/cross-project user preferences (brief communication, small increments, batching outside-repo writes, honest-capability-limits framing) rather than this project's content — left for Joakim to decide separately whether those belong in the global `claudefiles` config instead; not acted on unilaterally here since that's a different repo/scope than this fix.
- Cleared all 24 entries and the store's `MEMORY.md` index for this project once migration was confirmed — nothing left for a future session to accidentally rely on instead of the repo.
