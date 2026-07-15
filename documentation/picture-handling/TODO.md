# TODO — picture-handling

## Known drift

- **Database engine mismatch**: `requirements.txt` and `app/database.py`
  currently target MySQL (`mysql-connector-python`), but the intended
  engine going forward is **PostgreSQL**. Treat the current MySQL code as
  a draft, not the target. Migrate when database work resumes — don't
  build new features on top of the MySQL layer without checking first.
- `app/local_mysql.py` (gitignored credentials module) will need
  renaming/replacing once the Postgres migration happens.

## UI / core workflow

- Picker view: array of pictures in a chosen directory, three actions per
  picture — discard (move to discard dir), save (move to save dir,
  record original path), mark-and-save (move to mark dir, record
  original path).
- Grid layout as a reusable class: parameters for row/column count and
  thumbnail pixel size; adapt to screen size (see `screeninfo.get_monitors()`).
- Buttons for discard / mark / save with icons: red+trashcan,
  yellow+dotted square, green+floppy disk.
- Display counts: valid/invalid pictures and movies, number of
  thumbnails currently shown.
- Stacked, randomly-selected preview of a folder's pictures alongside the
  picture currently being worked on; replace consumed items from the
  stack; handle overflow gracefully when the folder has more pictures
  than fit on screen.

## Database

- Write to database; index all picture and movie files.
- Tag files: one table of distinct tags (with usage counts), a second
  table mapping tagID → mediaID.

## Object identification / AI

- Run LabelImg on the mark directory (manual button, later auto-run on
  "mark and save").
- Classify discard/save/mark directories to suggest sorting.
- Movie clip support (including whatever "4D" meant when this was
  jotted down — clarify before implementing).
- Compare pictures across directories to detect duplicates: by filename,
  by content (raw picture data — date, size), and by metadata.
