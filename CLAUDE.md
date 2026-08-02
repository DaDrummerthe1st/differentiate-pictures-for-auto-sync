# Working agreement

This file is the working agreement between Joakim and any AI session (or future human contributor) working in this repo. The repo is the memory — see the self-sufficiency rule in [WORKFLOW.md](documentation/policies/WORKFLOW.md).

This file itself stays a short index — full rule text, reasoning, and precedent live in the linked files. See [documentation/policies/POLICY.md](documentation/policies/POLICY.md) for hard constraints, [documentation/policies/WORKFLOW.md](documentation/policies/WORKFLOW.md) for how work happens session to session, and [documentation/README.md](documentation/README.md) for documentation structure.

## Starting a session

This file is the only doc guaranteed to be loaded automatically — it holds the rules, not the current state. Before assuming anything about where the project actually stands, read [documentation/README.md](documentation/README.md)'s folder index, then the relevant topic's own README/TODO — most carry a dated `Status:` line kept current for exactly this reason.

## Non-negotiables

- **Every technical/business term explained in conversation gets appended to [documentation/GLOSSARY.md](documentation/GLOSSARY.md), same turn, no exceptions.** Makes explaining things in chat (below) cheaper over time instead of re-explaining the same term ad hoc every session.
- **Explain research/technical findings fully in chat, every time — never just a pointer to the written docs.** The docs are the durable record; they don't substitute for actually explaining a finding to Joakim in the conversation itself.
- **Security and privacy first, every change** — hard constraints: [POLICY.md](documentation/policies/POLICY.md). Credentials handling specifically: [POLICY.md § Deployment and system access](documentation/policies/POLICY.md).
- **Test-Driven Development, no exceptions.** Full rule (what to run, when to skip a re-run): [WORKFLOW.md § Testing](documentation/policies/WORKFLOW.md).
- **This repo is fully self-sufficient — no external memory required.** Full statement: [WORKFLOW.md § Self-sufficiency](documentation/policies/WORKFLOW.md).
- **Ask or search — never guess.** Full statement: [WORKFLOW.md § Ask or search](documentation/policies/WORKFLOW.md).
- **Never claim an action was taken without checking the actual tool calls made that turn.** Full rule: [WORKFLOW.md § Traceable completion claims](documentation/policies/WORKFLOW.md).
- **A promised follow-up gets a TodoWrite item, not just a sentence.** Full rule: [WORKFLOW.md § Traceable completion claims](documentation/policies/WORKFLOW.md).
- **Documentation stays current with schema/API/architecture changes** — same pass, not deferred. Full rule: [documentation/README.md § Keeping docs current](documentation/README.md).
- **Every bug and AI-session process lapse is its own file.** Rule and tool: [documentation/bugs/README.md](documentation/bugs/README.md), [documentation/bugs/claude-bugs/README.md](documentation/bugs/claude-bugs/README.md).
- **Session wrap-up: full checklist and cadence** live in [documentation/tooling/README.md](documentation/tooling/README.md).
- **Commit/push discipline, branching and merging, high-blast-radius definitions, known permission-popup floors, dependency-freshness checks, argue-with-evidence, lean-and-compact doc philosophy, changelog/doc-metrics/commit-cost logging**: all in [WORKFLOW.md](documentation/policies/WORKFLOW.md) — the operational half of this working agreement.

## Documentation layout

Folder structure, `README.md`/`TODO.md` conventions, and formatting conventions (no hard-wrapping, etc.) are documented in [documentation/README.md](documentation/README.md), not here.
