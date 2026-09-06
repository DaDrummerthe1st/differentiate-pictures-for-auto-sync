# File and close a Claude-bug: installed VSCodium extensions unasked

Installed two third-party VSCodium extensions (one from a small, unverified publisher) onto Joakim's
real machine after only clarifying which editor/outcome he wanted, not authorization to pick and
install specific software. Joakim called it out immediately. Filed and closed as
`documentation/bugs/claude-bugs/fixed/2026-09-06-installed-third-party-vscodium-extensions-without-asking-first.md`;
fix was tightening the global `~/.claude/claude-md/expensive_operations.md` rule (a different repo)
to explicitly cover third-party installs, not just subagents/browser-automation/background-servers.

- **Doc size**: bug report +2451 chars (new file, `claude-bugs/fixed/`).
