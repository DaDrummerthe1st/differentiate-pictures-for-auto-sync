# Add field-scoped text search to the browse-contacts page

Joakim asked for search + "include/exclude" on the browse page; clarified the latter means the
search itself should be field-scoped (checkboxes for which fields to search in), not a content
filter. Added `contacts/search.py`: `available_search_fields()` offers `display_name`/`emails` plus
every `raw` key seen across stored contacts; `filter_contacts()` matches only within checked fields.
`render_browse_page()` gained the search form (plain GET, no JS); `handle_browse()` now takes the
request's query string, defaults to display_name+emails on a fresh page load, and respects an
explicit (possibly empty) field selection once the form is submitted. 8 new search tests, 5 new/
updated server tests; verified the URL-encoded-field-with-a-space case (e.g. "Organization Name")
directly since it's the one edge the unit tests didn't already cover implicitly.

- **Doc size**: contacts/README.md 5455 -> 6056 chars (+601).
