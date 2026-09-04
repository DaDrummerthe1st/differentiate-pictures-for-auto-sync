# Paginate test_main.py to fix X BadAlloc, add sample_test_pictures.sh

Adds `tools/sample_test_pictures.sh` (WIP): randomly copies N pictures from a chosen source
folder into `resources/test_pictures/` (already gitignored), with a manifest recording each
copy's original path. Running `test_main.py` against a real 100-photo sample this produced
crashed the X server (`BadAlloc` - it rendered every photo at once, ~300MB of pixmap memory in
one request); fixed by paginating (`IMAGES_PER_PAGE=20`, Prev/Next), which tears down the
previous page's images before building the next so memory stays bounded regardless of folder
size. Bug tracked in `documentation/bugs/repo/under_process/` pending Joakim's confirmation on
his own machine (this session had no display to verify the X-rendering path itself).

- **Doc size**: GLOSSARY.md +660, modules/README.md +217, new bug report +3645.
