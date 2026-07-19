# picture-handling/

Everything to do with viewing, sorting, labeling, deleting, and indexing
pictures and movie clips on a single local machine. **Superseded**: this
single-machine MVP/POC is resolved — active work moved to
[../photo-server/](../photo-server/README.md)'s multi-user web server.
Kept here as reference for what already exists and the MySQL-to-Postgres
migration note; see [TODO.md](TODO.md).

## What exists today

**On `master` only** — this branch (`mamma-photo-viewer`) is an orphan
branch with no shared git history with `master` (see
[photo-server/TODO.md](../photo-server/TODO.md)'s "Branch relationship"
section), so none of the files below exist in *this* branch's `app/`
directory, which instead holds the unrelated `mamma-photo-viewer` GUI
app (see [../gui/README.md](../gui/README.md)). Checked out `master` to
read this code.

- A directory picker (`app/utils/directory_picker.py`) and file-handling
  utilities (`app/file_handling.py`, `app/file_handling/`).
- EXIF/GPS metadata extraction (`app/gpsdata.py`).
- Object detection over a directory of images via a DNN model
  (`app/object_identification/obj_id.py`).
- A database layer (`app/database.py`) for indexing files and tags —
  currently wired to MySQL, see [TODO.md](TODO.md) for the intended
  target.

## Relevant external tools

Not adopted yet.

| Project | Site | Purpose |
| --- | --- | --- |
| LabelImg | https://github.com/tzutalin/labelImg | Manual labelling of picture regions/objects |
