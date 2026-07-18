# Used unexplained ad hoc labels instead of plain language

A routine that should have run per an existing rule, and didn't - or a
claim made without properly checking it first. See
[README.md](README.md) for what belongs here.

## What happened

2026-07-19, during a meta-discussion about session wrap-up cadence: this
session referred to two parts of its own reply as "thread 1" and "thread
2" without ever defining those labels in the text itself. Joakim had to
ask "What are thread 1 and thread 2?! Why do you come up with your own
names? Not being informational is a severe bug." — the labels only made
sense by re-deriving them from the surrounding paragraph structure, not
from anything actually stated.

## Why it happened

Reaching for a short internal label to refer back to earlier parts of a
long reply, the way a written outline would, without checking whether
that label was ever spelled out for the reader — a habit that works in
a document with visible headings, not in a chat reply where "thread 1"
carries no attached definition unless one is written out explicitly.

## What changed

No CLAUDE.md rule added specifically for this (the existing "Lean,
exact, and compact" and self-sufficiency principles already cover
"don't require the reader to re-derive meaning"). Behavioral correction
only: refer to things by what they actually are (e.g. "the wrap-up
check-cadence question" and "the session-length question") instead of
inventing numbered/labeled shorthand for parts of a reply, in this and
future sessions.
