# Record Pictures pipeline design and resolve YOLO-vs-NanoDet-Plus, SQLite, file_metadata questions

New `documentation/data-modeling/PICTURES_PIPELINE.md` records the three-session `modules/` pipeline Joakim sketched (file discovery → quality → prioritized object detection → scene classification → person grouping) plus decisions made resolving it: SQLite (not Postgres) for this standalone pipeline, NanoDet-Plus confirmed over YOLO (already excluded, AGPL-3.0) for object detection, `file_metadata` defined as filesystem stat data distinct from EXIF, and confirmation that `LogScenery()` is real — the already-researched, not-yet-built scene/venue classification in `curation/DETECTORS.md` area D. Added a `Filesystem metadata / stat data` glossary entry.

- **Doc size**: `documentation/data-modeling/PICTURES_PIPELINE.md` +3369 chars (new); `README.md` +217 chars; `TODO.md` +496 chars; `documentation/GLOSSARY.md` +748 chars.
