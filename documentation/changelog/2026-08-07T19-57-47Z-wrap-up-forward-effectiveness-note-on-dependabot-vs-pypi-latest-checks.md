# Wrap-up: forward-effectiveness note on Dependabot vs PyPI-latest checks

Per WORKFLOW.md's session wrap-up routine ("one concrete note on what would make the next session
cheaper or less error-prone"). This session's real friction: enabling Dependabot immediately
surfaced 50 pre-existing vulnerabilities in `pillow`/`python-multipart` that a plain "check PyPI for
the newest version" habit had missed — freshness and vulnerability-freeness are different questions.
Recorded into WORKFLOW.md's Dependency freshness section: future dependency checks should query
`gh api repos/<owner>/<repo>/dependabot/alerts?state=open` (or the Security tab) directly, not just
PyPI-latest.

- **Doc size**: `documentation/policies/WORKFLOW.md` +740 chars.
