# Group search-field checkboxes into collapsed categories

A flat checkbox per searchable field doesn't scale to a real Google export (121 columns). Added
`contacts/search.py::categorize_fields()` (Basic/Organization/Contact info/Name details/Other,
matched by keyword against each field's name) and had `render.py`'s search form render each
category as a collapsed native `<details>` instead of one long list. 6 new categorization tests.

- **Doc size**: contacts/README.md 6056 -> 6302 chars (+246).
