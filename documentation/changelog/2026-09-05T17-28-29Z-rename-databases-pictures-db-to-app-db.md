# Rename databases/pictures.db to app.db

`contacts/db.py` (next commit) needs a real SQLite file, and Joakim wants one shared database for
the whole app rather than one per module. Renamed `modules/pictures.py`'s `DEFAULT_DB_PATH` from
`pictures.db` to `app.db` — pure rename, no data migration needed, since the file is gitignored and
never existed on disk yet. `contacts/db.py` points at the same `app.db` with its own tables.

- **Doc size**: modules/README.md 3055 -> 3136 chars (+81), PICTURES_PIPELINE.md 8801 -> 9006 chars
  (+205).
