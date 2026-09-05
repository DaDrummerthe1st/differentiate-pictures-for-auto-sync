# Saving a contact with the same email under two CSV columns crashes on a UNIQUE constraint

Status: **investigating, not fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Joakim imported his real Google Contacts export in `contacts/web/server.py`, the preview rendered
correctly, but clicking "Save to database" crashed the server with:

```
sqlite3.IntegrityError: UNIQUE constraint failed: contact_emails.contact_id, contact_emails.email
```

Traceback pointed at `contacts/db.py`'s `_apply()`, in the loop that inserts each of a new
contact's emails into `contact_emails`.

## Investigation log

1. `contact_emails` has `UNIQUE(contact_id, email)` — inserting the same `(contact_id, email)` pair
   twice in one transaction raises exactly this error.
2. `parse_google_csv()` builds a contact's `emails` list from every `E-mail N - Value` column on the
   row (`google_csv_import.py`), with no dedup. A real Google export can carry the same address
   under two differently-labeled email columns (e.g. relabeled Home/Other, or a leftover duplicate
   from a past manual edit) — plausible and apparently what Joakim's real export contains, since the
   crash only appeared once he tried it, never against any synthetic fixture.
3. Reproduced directly: a `Contact` with `emails=["alice@example.com", "alice@example.com"]` (either
   from that CSV column duplication, or literally any importer producing a repeated value) crashes
   `save_contacts()` the same way — confirmed via `contacts/tests/test_db.py`'s new
   `test_a_contact_with_duplicate_emails_in_its_own_list_does_not_crash_the_insert`.
4. Traced the "new contact" path specifically: `contacts/db.py::_classify()`'s no-match branch set
   `merged_emails=list(contact.emails)` — a plain copy, no dedup — while the "matched" branch two
   lines below already did `list(dict.fromkeys(existing.emails + contact.emails))`. The dedup
   existed on one branch and was simply missing on the other.

## Fix

Two changes, matching the two places a duplicate could originate:
- `contacts/google_csv_import.py`: dedupe a row's emails at the source (`dict.fromkeys(...)`,
  order-preserving) — the actual cause of Joakim's crash.
- `contacts/db.py::_classify()`'s "new contact" branch: `merged_emails=list(dict.fromkeys(contact.emails))`
  instead of a plain `list(...)` — defense in depth, so `save_contacts()` can't be crashed by a
  duplicate-emails `Contact` regardless of which importer (or future one) produced it.

## Verified

Two new regression tests (`contacts/tests/test_google_csv_import.py`,
`contacts/tests/test_db.py`) reproduce the exact failure and pass after the fix; full suite (91
tests) passes. Also reproduced the original crash scenario end-to-end through
`contacts.web.server.handle_preview()`/`handle_save()` with a synthetic two-column-same-email CSV
(never Joakim's real file) — confirmed no crash and exactly one stored email afterward.

## Security analysis

The fix only changes which values get deduplicated before an `INSERT` — it doesn't change what data
is read, stored, or exposed, and touches no authentication, authorization, or external-facing
surface. The affected code path only ever runs against a file the user chose in their own browser,
processed entirely by their own local server (127.0.0.1). No residual risk identified.
