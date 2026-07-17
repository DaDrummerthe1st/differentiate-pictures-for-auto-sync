# Wrong claim about loading="lazy" from a grep bug

## What happened

Told Joakim thumbnails weren't lazy-loaded ("that's not implemented
yet"), based on `grep -n "loading="` finding nothing. The actual code
had `imgEl.loading = "lazy"` — spaces around the `=` that the grep
pattern didn't account for, so it silently missed a real match instead
of erroring. The claim was corrected in the same turn once the code was
read directly, but it went out first.

## Why it happened

Trusted a single grep result as sufficient evidence for a definitive
claim ("that's not implemented") instead of reading the actual code
before stating something as fact.

## What changed

None yet as a concrete rule change — logged as a general practice to
apply going forward: before asserting "X isn't implemented" from a
negative search result, read the relevant code directly rather than
trusting one grep pattern - a missed match looks identical to a true
negative.
