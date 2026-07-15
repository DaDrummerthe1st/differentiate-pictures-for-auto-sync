# TODO — picture-handling

## First MVP/POC — resolved, moved to photo-server/

The "what's the specific purpose" question below was answered: it's a
multi-user web server (browse/search/tag/download), not a local desktop
tool. That decided the UI/core-workflow, database (tags), and object-
identification sections that used to live here — they're superseded by
[../photo-server/](../photo-server/README.md), not built here. See that
folder's TODO.md for the actual roadmap, DATA_DICTIONARY.md for the tag
schema (tag-based albums, not move-to-directory discard/save/mark), and
DEFERRED.md / [../VISION.md](../VISION.md) Pillar 2 for why
AI/object-identification is deferred to on-device, phone-side inference
rather than the server-side LabelImg/DNN approach originally sketched
here.

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
- **Unverified dependency bump (2026-07-15)**: `requirements.txt` was
  pinned to the latest CVE-checked versions of everything it lists
  (numpy 2.5.1, opencv-python 5.0.0.93, Pillow 12.3.0, exif 1.6.1,
  python-magic 0.4.27, mysql-connector-python 9.7.0) — see CHANGELOG.md
  for the CVEs this closes. numpy 2.x and opencv-python 5.x are **major**
  version jumps from whatever 1.x/4.x was actually installed before
  (numpy 2.x has an ABI break and removed ~100 namespace members; see
  https://numpy.org/devdocs/numpy_2_0_migration_guide.html). This
  environment has no `pip` to install and actually run `app/` against
  the new pins, so **this is unverified** — run
  `pip install -r requirements.txt` and exercise `app/object_identification/obj_id.py`
  (the DNN/numpy/opencv code most likely to break) on a machine with pip
  before trusting this update.
