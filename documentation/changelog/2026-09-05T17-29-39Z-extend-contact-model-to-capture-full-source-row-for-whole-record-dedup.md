# Extend Contact model to capture full source row for whole-record dedup

Joakim's dedup rule for re-imported contacts ("compare the whole row, not just email/display_name")
needed the data to actually compare — `Contact` previously only kept `display_name`/`emails`/
`source`, discarding everything else (phone, organization, notes, ...). Added `Contact.raw: dict`,
populated by both importers: `google_csv_import.py` keeps the full `csv.DictReader` row;
`vcard_import.py` flattens every other vCard property (`card.contents`) into a matching dict. TDD:
2 new tests confirming `raw` is actually populated from real rows/vcards.

- **Doc size**: no docs changed (contacts/README.md updated in the next commit alongside the
  persistence layer that consumes `raw`).
