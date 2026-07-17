# bugs/claude/LOG.md

See [README.md](README.md) for what belongs here. Newest first.

## 2026-07-17 — Missed doc_metrics/commit_cost logging for 3 commits

After the session's earlier wrap-up round, three more commits went out
(`cca8a47`, `6b3315d`, `41a2073`) without the `tools/doc_metrics`/
`tools/commit_cost` logging step that CLAUDE.md requires after every
commit. Joakim caught the gap by asking directly, not something I
noticed myself.

**Why it happened**: mid-session momentum — several fast-moving fixes in
a row (a bug report correction, then a policy add-then-revert cycle) and
the logging step quietly stopped being part of the loop, with no
explicit checkpoint forcing it back in.

**What changed**: none yet, beyond running it late and confirming the
gap. Worth considering whether the routine needs a harder trigger than
"remember after every commit" during fast multi-commit stretches — e.g.
batching the metrics-logging commit less eagerly is already how this
project works when time is short, but that shouldn't mean *skipping* it
entirely for 3+ commits unnoticed.

## 2026-07-17 — Wrong claim about `loading="lazy"` from a grep bug

Told Joakim thumbnails weren't lazy-loaded ("that's not implemented
yet"), based on `grep -n "loading="` finding nothing. The actual code
had `imgEl.loading = "lazy"` — spaces around the `=` that the grep
pattern didn't account for, so it silently missed a real match instead
of erroring. The claim was corrected in the same turn once the code was
read directly, but it went out first.

**Why it happened**: trusted a single grep result as sufficient
evidence for a definitive claim ("that's not implemented") instead of
reading the actual code before stating something as fact.

**What changed**: none yet. Worth a general practice, not just a
one-off fix: before asserting "X isn't implemented" from a negative
search result, read the relevant code directly rather than trusting one
grep pattern - a missed match looks identical to a true negative.

## 2026-07-17 — Assumed instead of asked on an ambiguous instruction

Joakim wrote "DO NOT WRITE ANYTHING IN LOCAL STORAGE for claude!!" and
it was read as being about browser `localStorage` in the photo-viewer
app (since that word had just appeared in a bugs/TODO.md write-up).
He actually meant something different: not persisting durable
instructions only to the AI's own local/private memory instead of the
repo. This produced a POLICY.md addition and a bugs/TODO.md edit that
then had to be fully reverted once he clarified.

**Why it happened**: the emphatic, all-caps phrasing read as urgent
enough to act on immediately, and "localStorage" had a recent, literal,
plausible match in context (my own just-written suggestion) - that
surface-level match was trusted over checking whether it actually fit
what was being reacted to.

**What changed**: none yet. This project's own non-negotiable is "ask or
search, never guess" for uncertain facts - worth explicitly extending
that instinct to ambiguous *instructions* under time pressure too, not
just uncertain facts, especially for anything that writes to a policy
file. A single clarifying question would have cost less than the
write-then-revert cycle.
