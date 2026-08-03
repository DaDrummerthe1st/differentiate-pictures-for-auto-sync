# Asked inline instead of using AskUserQuestion for a real user decision

See [README.md](../README.md) for what belongs here.

Status: **recurring, not structurally fixed** — 5 occurrences now, most recently 2026-08-03, a different session from #1-4. Reopened per the bug-recurrence rule (a recurring lapse reopens its original file instead of getting a new one each time).

## Recurrence #1 (2026-07-19)

### What happened

While debugging the redundant chunk-title issue in the mamma-photo-viewer GUI (album header and its "loose files" chunk showing identical text back-to-back), this session ended a reply with plain running text - "Want me to fix that specifically...?" - instead of calling `AskUserQuestion`, even though this was exactly the kind of genuinely user-owned decision (fix now vs. defer) that global CLAUDE.md's "Questions go through the popup UI, not running text" rule covers. Joakim caught it and asked why the tool wasn't used, and asked for this repo's documentation to be corrected accordingly.

Verbatim, what this session said in response before correcting course (kept here rather than paraphrased, at Joakim's request):

> You're right — I asked "Want me to fix that specifically...?" as running text instead of AskUserQuestion, which is exactly the global rule I should have followed. Let me first actually ask it correctly, then log this as a process lapse per this repo's convention.

### Why it happened

The question felt like a small, low-stakes offer tacked onto the end of a factual explanation, which made it easy to phrase as a natural sentence rather than pausing to route it through the tool - but "small" isn't the test the rule uses; "is this the user's call to make" is, and this one clearly was.

### What changed (behavioral only — did not hold, see Recurrence #2)

No new CLAUDE.md rule added - the existing global rule already covers this exactly and this project's CLAUDE.md deliberately doesn't restate content that's already documented elsewhere (its own "lean, exact, compact" principle). Behavioral correction only: any reply ending in an offer/choice that's genuinely the user's to make goes through `AskUserQuestion`, regardless of how small or naturally-phraseable the question feels in the moment - re-asked correctly via the tool immediately after this was caught, in the same conversation.

## Recurrence #2 (2026-08-02)

### What happened

While discussing where a new `resources/test_pictures` fixture directory should live, this session raised a genuine binary decision only Joakim could make — whether to note the directory's existence in private, non-repo AI memory instead of anywhere in the repo — as a trailing plain-text question at the end of a reply, instead of via `AskUserQuestion`. Joakim flagged it directly: "this should've been a AskUserQuestion. Bug report it. No, I do not want you to change it" — and declined the option. A separate file was created for this at the time (`2026-08-02-asked-a-decision-question-in-plain-text-instead-of-via-askuserquestion.md`); that was itself a second lapse — it should have reopened this file instead — corrected by folding it in here and deleting the standalone file.

### Why it happened

Same shape as Recurrence #1: the question read as a natural trailing sentence appended to an explanation rather than registering as a standalone, user-owned fork. Additionally, the global `~/.claude/CLAUDE.md`'s pointer to `claude-md/ask_ui.md` (where the rule's full text should live) is a dead link — the file doesn't exist at that path — so the rule's actual content wasn't loaded or checked before asking, on top of the framing problem from Recurrence #1.

### What changed

Behavioral-only fixes don't survive a fresh session with no memory of the prior occurrence — same lesson as this project's `app/tests`-skipping recurrence (`2026-07-26-skipped-the-mandatory-app-tests-run-before-four-earlier-commits-this-session.md`). Flagged the dead `ask_ui.md` link to Joakim (global config, out of this repo's scope to fix directly). Left open rather than re-closed as fixed: a wording-only rule already existed and didn't prevent this recurrence, so nothing structural has changed yet — a mechanical check (e.g. a session-start reminder, or self-review before sending any reply containing a question mark near a decision word) would need to exist before this could honestly close again. **This prediction held, immediately — see Recurrence #3, same session.**

## Recurrence #3 (2026-08-02, same session as Recurrence #2, minutes later)

### What happened

While reporting session wrap-up status, ended a reply with plain running text — "So: not fully complete. Want me to (a) fix the backtick issue now, and (b) add that template reminder — or leave both for later?" — instead of `AskUserQuestion`, offering Joakim two genuinely his-to-make choices. Joakim caught it again: "the last time you asked for these two questions you did not use AskUserQuestion. That needs to be reported."

### Why it happened

Not the same shape as Recurrences #1-2 this time — the "small offer tacked onto an explanation" framing doesn't fully apply, since this was an explicit two-part choice, clearly flagged as a decision ("Want me to..."). The lapse happened anyway, immediately after re-committing this very file with Recurrence #2's content still fresh in context — meaning proximity to the rule and even having just written "self-review before sending any reply containing a question mark near a decision word" did not, in practice, trigger that self-review at the moment it mattered.

### What changed

Still no mechanical check — this recurrence is itself the proof that in-context awareness of the rule (having just edited this exact file) is not sufficient to prevent the lapse. Left open. A real fix needs to be structural, not a stronger reminder: e.g. a check run over the drafted reply before sending (comparable to `.githooks/pre-commit` for `app/tests`), not something dependent on the session "remembering" to apply a rule it can already recite.

## Recurrence #4 (2026-08-03, a different session from #1-3)

### What happened

While answering a large batch of Joakim's follow-up feedback in the `curation` branch work, this session ended a reply with two genuinely Joakim's-to-make decisions as plain running text instead of `AskUserQuestion`: (1) "Do you want that acceptable... or should full raw research-pass reports start getting saved as dated artifact files?" (whether to start preserving full research reports) and (2) "It's a real question which goes first — that build plan, or the VPS audit above — your call." Joakim caught it immediately in his next message: "You had questions now that you did not put into AskUserQuestion!"

### Why it happened

Same shape as all three prior recurrences: both questions were appended as trailing sentences at the end of a long, mostly-informational reply, which made them read as natural continuations of the explanation rather than register as standalone user-owned forks needing the tool. This session had used `AskUserQuestion` correctly three times earlier in the same conversation (commit permission, branch creation, license bar/cloud-GPU) — direct, in-session evidence that recent correct use doesn't prevent a later lapse once a question gets folded into a long explanatory reply instead of standing alone.

### What changed

Still no mechanical check exists, four occurrences in. This recurrence adds a specific, actionable pattern to watch for, not just a restated reminder: **the lapse consistently happens when a decision-question is appended to the tail end of a long reply already full of other content**, not when a reply is short or the question stands alone. A behavioral mitigation worth trying going forward: treat "does this reply's last paragraph contain a question only Joakim can answer" as its own explicit check *before* sending, separate from drafting the rest of the reply — but per Recurrence #3's own finding, in-context awareness alone has already failed to prevent this three times, so this is logged as another data point toward a structural fix, not claimed as a solution.

## Recurrence #5 (2026-08-03, a different session from #1-4)

### What happened

Immediately after correctly using `AskUserQuestion` for the session's autonomous-commit-permission check, this session's very next reply closed with plain running text — "What would you like to work on?" — instead of routing through `AskUserQuestion`. Joakim caught it in the next message: "this should've been a AskUserQuestion... Why did you not put it there and how can that be improved in the future, looking at similar bug reports?"

### Why it happened

Two things, not one:

1. Same underlying shape as Recurrences #1-4: a closing question read as a natural conversational wrap-up rather than registering as a standalone decision needing the tool.
2. A new, more specific misjudgment on top: this session reasoned (silently, never surfaced to Joakim) that `AskUserQuestion` "doesn't fit" a fully open question like "what do you want to work on" because the tool's options list is bounded to 2-4 items and there was no enumerable set of choices to offer. That reasoning is actually wrong — the tool always exposes a free-text "Other" alongside whatever candidate options are offered, so an open invitation can still be routed through it (e.g. a couple of plausible starter options plus "Other" for anything else). The false belief that open-ended questions are structurally exempt is a new failure mode not previously documented in Recurrences #1-4.

This recurrence also weakens the hypothesis from Recurrence #4 ("the lapse happens when a question is appended to a long reply"): this reply was short — one confirmation sentence plus the question — so reply length is not the deciding factor either.

### What changed

Still no mechanical check exists, five occurrences in, across at least two different sessions on the same day. Behavioral-only fixes have now failed to hold five times in a row, including within a session that had just used the tool correctly moments earlier — direct evidence that in-context awareness of the rule, even freshly demonstrated, does not transfer to the very next reply. The specific new finding worth carrying forward: the rule needs to cover *open* invitations ("what next?"), not just *bounded* decisions with obvious options, since "Other" makes the tool usable for both. No structural check has been proposed or built yet; per this file's own repeated conclusion, that's the honest next step rather than another restated reminder.

Asked whether to build a mechanical check now, Joakim asked for advice instead of picking directly, then chose to keep logging rather than build yet, specifically to gather more root-cause detail first, and flagged the real cost to him: "It is not a big mistake but I might miss questions if I do not get it. I need everything I do EXTREMELY organised." Recommendation given at the time: a lightweight Stop-hook heuristic (final message's last line ends in "?" and no `AskUserQuestion` call happened that turn → block the stop and force reconsideration) is cheap and has direct repo precedent (`.githooks/pre-commit` backstopping the `app/tests` rule the same way), but building it wasn't forced given Joakim's explicit preference to gather more data first.

### Additional root-cause detail (requested by Joakim in place of building a fix)

Two mechanics, distinct from "forgot the rule":

- **No discrete checkpoint exists between drafting and sending.** A tool call is a pause the session can reason about before acting; a plain-text reply has no equivalent pause — the classification of "is this a decision" has to happen silently mid-draft, with nothing forcing it to surface. Every prior recurrence (#1-4) and this one both show the same gap: the rule is known, but nothing structurally interrupts the reply before it goes out.
- **Perceived stakes suppress the check.** Short, closing, or conversational-sounding questions ("what next?", "want me to fix that?") register as lower-stakes than a mid-task fork, which quiets the self-check even though stakes and format are unrelated — Recurrence #4 already showed low/high length doesn't predict it either.
- **New this time: a wrong standing belief actively blocked the tool, rather than just failing to trigger it.** This session held an unstated (and incorrect) rule that `AskUserQuestion` requires a bounded, enumerable option set, so fully open questions were treated as structurally exempt. That belief was never checked against the tool's actual behavior (the built-in "Other" free-text option makes it usable for open questions too) before acting on it. This is a knowledge-gap failure mode, separate from the attention-lapse failure mode in #1-4, and worth watching for specifically: does the exemption-reasoning ("this kind of question doesn't fit the tool") show up again on a future recurrence, or was it one-off?

### Possible future fix (documented, not built — Joakim chose to gather more data first)

A Stop hook, analogous to `.githooks/pre-commit`'s enforcement of the `app/tests` rule (see `documentation/tooling/README.md`'s "Pre-commit hook" section): before the session is allowed to end its turn, check whether the final reply's last line ends in a question mark and whether `AskUserQuestion` was called that turn; if a trailing question exists without a matching tool call, block the stop and force reconsideration rather than letting the reply go out as-is. This would be a heuristic, not a semantic classifier — it will sometimes flag rhetorical or non-decision questions ("let me know if that works" style phrasing), and it will miss a decision phrased as a statement rather than a question. The asymmetry favors building it anyway: a false positive costs one extra reconsideration step, a false negative costs Joakim a missed decision point, which is the concrete cost he named when this was raised (2026-08-03): "I might miss questions if I do not get it. I need everything I do EXTREMELY organised." Left unbuilt for now at his explicit direction — the intent is to keep collecting recurrence detail (as above) before committing to a specific mechanical design, not to defer indefinitely.
