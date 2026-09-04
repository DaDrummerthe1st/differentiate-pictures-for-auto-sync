# Shared list of commit-message titles that mark a commit as a doc_metrics/
# commit_cost ledger catch-up (only ledger files staged, no real changes).
# Sourced by both commit-msg (to allow/police these titles) and post-commit
# (to recognize one so its self-recursion guard doesn't re-trigger on it).
# Kept in one place after a real bug: post-commit only recognized the first
# of these three, so a manual catch-up titled with either of the other two
# caused a spurious follow-up commit — see
# documentation/bugs/repo/fixed/2026-09-05-post-commit-hook-s-self-recursion-guard-only-recognizes-one-of-the-three-commit-msg-allowed-catch-up-titles-SOLVED.md
CATCH_UP_TITLES=(
  "Log doc metrics and commit cost for the previous commit"
  "Log commit cost for the previous commit"
  "Log doc metrics for the previous commit"
)

is_catch_up_title() {
  local candidate="$1" title
  for title in "${CATCH_UP_TITLES[@]}"; do
    [ "$candidate" = "$title" ] && return 0
  done
  return 1
}
