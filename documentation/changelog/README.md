# changelog/

One file per entry — not a shared growing file. Replaces the old single-file `CHANGELOG.md`, now frozen as [CHANGELOG_ARCHIVE.md](../../CHANGELOG_ARCHIVE.md). That file broke under concurrent-branch merges: a single growing file with multi-line prose entries is exactly the shape git's line-based merge handles worst (see [documentation/bugs/claude-bugs/under_process/2026-07-23-changelog-header-paragraph-silently-displaced-by-a-naive-top-insert.md](../bugs/claude-bugs/under_process/2026-07-23-changelog-header-paragraph-silently-displaced-by-a-naive-top-insert.md) for the incident that forced this).

Pattern borrowed from [bugs/](../bugs/README.md) (already proven here) and from Towncrier/Changesets' fragment-file model — the tools themselves don't fit (Changesets needs a Node/npm toolchain this repo deliberately has none of; Towncrier assumes versioned releases, which this continuously-deployed repo doesn't have), but the "one file per change" pattern does.

Use `tools/create_changelog_entry/create_changelog_entry.sh "Short title"` to create one with a consistent name and starter template — don't hand-name these.

## Filename convention

`<UTC-ISO-8601-timestamp-no-colons>-<slug>.md`, e.g. `2026-07-23T16-45-12Z-rebuild-changelog.md`. Sub-day precision because multiple entries per day are common — day-only precision, like `bugs/` uses, wouldn't sort correctly. The script stamps this automatically; never hand-name a file here.

## One entry, many parts of the system

A single entry file can cover multiple parts of the system in one revision (GUI + backend in one file) — the file boundary is "one revision," not "one subsystem." Confirmed against real precedent: Changesets' interactive CLI lets one changeset target multiple packages; Towncrier merges fragments referencing multiple issues into one entry.

## Entry content

What + why, one or two lines — same discipline the old `CHANGELOG.md` used. Report the character-count change for any documentation edited, per [CLAUDE.md](../../CLAUDE.md).

## No index

No index file is kept, same reasoning as `bugs/` (tried once at that level, drifted out of sync, removed). `ls documentation/changelog/` (sorted, or `-t` for newest-first) gives the same view an index would.

## Browsable view

Deferred — see [TODO.md](TODO.md). Not required to start; `bugs/` proves `ls`-and-read works without one.
