# picture-handling/

Everything to do with viewing, sorting, labeling, deleting, and indexing
pictures and movie clips on a single local machine. This is the current
phase of work — see [TODO.md](TODO.md) for open items.

## What exists today

- A directory picker (`app/utils/directory_picker.py`) and file-handling
  utilities (`app/file_handling.py`, `app/file_handling/`).
- EXIF/GPS metadata extraction (`app/gpsdata.py`).
- Object detection over a directory of images via a DNN model
  (`app/object_identification/obj_id.py`).
- A database layer (`app/database.py`) for indexing files and tags —
  currently wired to MySQL, see [TODO.md](TODO.md) for the intended
  target.

## Relevant external tools

| Project | Site | Purpose | In use? |
| --- | --- | --- | --- |
| LabelImg | https://github.com/tzutalin/labelImg | Manual labelling of picture regions/objects | Not yet |
