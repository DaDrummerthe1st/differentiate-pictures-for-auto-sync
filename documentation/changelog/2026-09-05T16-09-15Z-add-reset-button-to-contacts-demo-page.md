# Add reset button to contacts demo page

Joakim asked for a way to clear the demo's loaded contacts back to the empty state without
reloading the page. Added a "Reset" button next to "Simulate a rename" — clears `contacts` and
`previousSnapshot`, clears the file input (so re-picking the same file re-triggers `change`), and
restores the "No contacts loaded yet." status.

- **Doc size**: no docs changed.
