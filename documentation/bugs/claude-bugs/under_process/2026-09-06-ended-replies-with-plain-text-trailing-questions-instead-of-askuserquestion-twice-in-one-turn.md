# Ended replies with plain-text trailing questions instead of AskUserQuestion, twice in one turn

See [README.md](../README.md) for what belongs here.

## What happened

During a discussion session on the native-app pivot's home-NAS/networking design, one reply ended
with a plain-text trailing question ("is full router-replacement something you want to require for
v1... or should v1 assume NAS-as-LAN-device...") instead of `AskUserQuestion`. Joakim answered it
inline anyway, moving the discussion forward, then a *second* reply in the same discussion thread
ended with another plain-text trailing question ("does that framing match what you mean, or would
you phrase the rule differently?"). Joakim caught both and asked for this to be logged as a bug.

## Why it happened

The exact structural failure `feedback_trailing_questions_need_askuserquestion.md` already names:
no checkpoint between drafting a reply and sending it, so a natural-sounding closing question slips
out as prose. This makes it (at least) the seventh recorded recurrence of this same lapse in this
project, well past the sixth instance that memory file already cites — proof that a purely
declarative memory entry, however clearly worded, isn't sufficient on its own to prevent this class
of mistake; the check has to happen at send-time, not be recalled from a prior write-up.

## What changed

- Updated `feedback_trailing_questions_need_askuserquestion.md` with this instance and the revised
  recurrence count.
- Flagged to Joakim (not unilaterally built, since it's a separate piece of engineering outside
  this session's actual discussion) that a mechanical fix may now be warranted given a documented
  memory alone has not stopped this after seven occurrences — e.g. a `Stop`-event hook that scans
  the assistant's final message for a trailing `?` outside of an `AskUserQuestion` tool call and
  blocks/forces a redo. Not implemented this session; a decision for Joakim on whether it's worth
  the added friction of a hook that can misfire on a rhetorical, non-decision question.
