# Add location lookup queries to modules/pictures.py for the web viewer

Second step of the browser-based pictures viewer: since it browses the SQLite pictures/locations
register (databases/app.db) rather than re-walking a folder on every request, added `get_location`
(one location by id, for the per-picture detail page) and `list_locations_under` (every registered
location inside a folder, sorted by path, for the grid view) to modules/pictures.py. Both tested.

- **Doc size**: no docs changed.
