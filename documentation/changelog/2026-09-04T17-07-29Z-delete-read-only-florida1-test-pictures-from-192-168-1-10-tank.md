# Delete read-only Florida1 test-pictures from 192.168.1.10:/tank/

`resources/test_pictures/Florida1` (untracked, gitignored, sourced from `192.168.1.10:/tank/`) was mode `0555` (no write bit) on both the directory and its `Florida/` subdirectory, so `rm -r` failed until `chmod -R u+w` was applied first. Deleted from the `test_production1` checkout; confirmed the `master` checkout at `/home/joakim/code/resources/differentiate-pictures-for-auto-sync` never had `resources/test_pictures/` on disk, so no copy remains there.

- **Doc size**: +2 lines
