# Fix post-commit hook's self-recursion guard to recognize all three catch-up commit titles

While catching up a genuinely missing `commit_cost` row for an earlier commit, hand-committing the
ledger fix under the title `commit-msg` explicitly allows ("Log commit cost for the previous
commit") triggered a spurious extra auto-commit from `post-commit`, because its self-recursion
guard only ever recognized one of the three titles `commit-msg` accepts. Extracted the three titles
into a new shared `.githooks/catch_up_titles.sh`, sourced by both hooks, so they can't drift apart
again. Verified in an isolated throwaway clone (no real push): the previously-broken title no
longer produces a follow-up commit, and the next real commit still closes the ledger gap correctly.
Filed as [documentation/bugs/repo/fixed/2026-09-05-...-SOLVED.md](../bugs/repo/fixed/2026-09-05-post-commit-hook-s-self-recursion-guard-only-recognizes-one-of-the-three-commit-msg-allowed-catch-up-titles-SOLVED.md).

- **Doc size**: new bug report file, 4982 chars.
