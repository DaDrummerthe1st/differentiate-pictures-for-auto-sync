# Collapse search-field checkboxes behind an Advanced search toggle

Joakim wanted the categorized field checkboxes tucked away too, not just grouped. Wrapped the whole
`search-fields` fieldset in a collapsed `<details class="advanced-search">` — the text box and
Search button stay always visible; the per-field checkboxes only appear once "Advanced search" is
expanded. One new render test.

- **Doc size**: no docs changed.
