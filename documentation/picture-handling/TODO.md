# TODO — picture-handling

## First MVP/POC — resolved, moved to photo-server/

The "what's the specific purpose" question below was answered: it's a
multi-user web server (browse/search/tag/download), not a local desktop
tool. That decided the UI/core-workflow, database (tags), and object-
identification sections that used to live here — they're superseded by
[../photo-server/](../photo-server/README.md), not built here. See that
folder's TODO.md for the actual roadmap, DATA_DICTIONARY.md for the tag
schema (tag-based albums, not move-to-directory discard/save/mark), and
DEFERRED.md/DPFAS_VISION.md for why AI/object-identification is deferred
to on-device, phone-side inference rather than the server-side LabelImg/
DNN approach originally sketched here.

## Known drift

- **Database engine mismatch**: `requirements.txt` and `app/database.py`
  currently target MySQL (`mysql-connector-python`), but the intended
  engine going forward is **PostgreSQL**. Treat the current MySQL code as
  a draft, not the target. Migrate when database work resumes — don't
  build new features on top of the MySQL layer without checking first.
  (photo-server/ is a fresh stack and made the Postgres choice
  independently — same conclusion, unrelated codebase.)
- `app/local_mysql.py` (gitignored credentials module) will need
  renaming/replacing once the Postgres migration happens.
