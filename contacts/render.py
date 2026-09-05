"""Server-side HTML rendering for contacts/web/server.py.

Deliberately no client-side JS for any of this: grouping, diffing, and
classification are all Python (contacts/db.py); this module turns that data
into plain HTML. The two-level collapse (letter group, then each contact
card) uses native <details>/<summary> - no JS needed for that either.
"""
import json

from contacts.db import ClassifyResult, StoredContact

_PAGE_STYLE = """
body { font-family: sans-serif; max-width: 760px; margin: 2rem auto; color: #222; }
h1 { margin-bottom: 0.3rem; }
.note { color: #555; font-size: 0.9em; }
nav { margin: 1rem 0; }
nav a { margin-right: 1rem; }
form.upload { margin: 1.5rem 0; padding: 1rem; border: 1px solid #ddd; border-radius: 6px; }
button, input[type=submit] { padding: 0.5rem 1rem; cursor: pointer; }
.summary { background: #f4f4f4; padding: 0.6rem; border-radius: 4px; margin-bottom: 1rem; }
details.letter-group { border: 1px solid #ddd; border-radius: 4px; margin-bottom: 0.4rem; }
details.letter-group > summary {
  cursor: pointer; font-weight: bold; padding: 0.5rem 0.7rem; background: #f0f0f0;
  border-radius: 4px; list-style: none;
}
details.letter-group > summary::-webkit-details-marker { display: none; }
details.letter-group > summary::before { content: '\\25B8 '; }
details.letter-group[open] > summary::before { content: '\\25BE '; }
details.contact-card { border-top: 1px solid #eee; }
details.contact-card > summary {
  cursor: pointer; padding: 0.4rem 0.7rem 0.4rem 1.4rem; list-style: none;
  display: flex; align-items: center; gap: 0.5rem;
}
details.contact-card > summary::-webkit-details-marker { display: none; }
details.contact-card > summary::before { content: '\\25B8'; font-size: 0.8em; color: #888; }
details.contact-card[open] > summary::before { content: '\\25BE'; }
.card-body { padding: 0 0.7rem 0.7rem 1.9rem; font-size: 0.9em; }
.card-body dl { margin: 0.3rem 0 0; display: grid; grid-template-columns: max-content 1fr; gap: 0.15rem 0.6rem; }
.card-body dt { color: #666; }
.diff-old { color: #a33; text-decoration: line-through; }
.diff-new { color: #276b27; font-weight: bold; }
.badge { font-size: 0.75em; padding: 0.1rem 0.5rem; border-radius: 10px; font-weight: normal; }
.badge-new { background: #d4edda; color: #276b27; }
.badge-updated { background: #fff3cd; color: #7a5c00; }
.badge-unchanged { background: #e2e3e5; color: #555; }
"""

_BADGE_TEXT = {"new": "NEW", "updated": "UPDATE", "unchanged": "UNCHANGED"}


def escape_html(s) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def group_by_first_letter(items: list, key) -> dict:
    groups: dict[str, list] = {}
    for item in items:
        name = key(item).strip()
        letter = name[0].upper() if name else "#"
        groups.setdefault(letter, []).append(item)
    for letter in groups:
        groups[letter].sort(key=lambda i: key(i))
    return {letter: groups[letter] for letter in sorted(groups)}


def render_field_diff(old_value, new_value) -> str:
    old_display = escape_html(old_value) if old_value else "(none)"
    new_display = escape_html(new_value) if new_value else "(none)"
    if old_value == new_value:
        return new_display
    return f'<span class="diff-old">{old_display}</span> → <span class="diff-new">{new_display}</span>'


def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{escape_html(title)}</title>
<style>{_PAGE_STYLE}</style>
</head>
<body>
<nav><a href="/">Import</a> | <a href="/contacts">Browse all contacts</a></nav>
{body}
</body>
</html>
"""


def _raw_table(raw: dict, existing_raw: dict | None) -> str:
    if not raw and not existing_raw:
        return "<dt>Other fields</dt><dd>(none)</dd>"
    keys = sorted(set(raw) | set(existing_raw or {}))
    rows = []
    for key in keys:
        new_value = raw.get(key)
        if existing_raw is not None:
            value_html = render_field_diff(existing_raw.get(key), new_value)
        else:
            value_html = escape_html(new_value)
        rows.append(f"<dt>{escape_html(key)}</dt><dd>{value_html}</dd>")
    return "\n".join(rows)


def _render_classify_card(result: ClassifyResult) -> str:
    contact = result.contact
    badge = f'<span class="badge badge-{result.status}">{_BADGE_TEXT[result.status]}</span>'
    name_html = (
        render_field_diff(result.existing.display_name, contact.display_name)
        if result.existing else escape_html(contact.display_name)
    )
    emails_html = (
        render_field_diff(", ".join(result.existing.emails), ", ".join(result.merged_emails))
        if result.existing else escape_html(", ".join(contact.emails) or "(none)")
    )
    matched_by_text = {
        "email": "email", "display_name": "display name", None: "(no match — new contact)",
    }[result.matched_by]
    raw_rows = _raw_table(contact.raw, result.existing.raw if result.existing else None)

    return f"""<details class="contact-card">
<summary>{escape_html(contact.display_name)} {badge}</summary>
<div class="card-body">
<dl>
<dt>Display name</dt><dd>{name_html}</dd>
<dt>Email(s)</dt><dd>{emails_html}</dd>
<dt>Source</dt><dd>{escape_html(contact.source or "(unknown)")}</dd>
<dt>Matched by</dt><dd>{matched_by_text}</dd>
{raw_rows}
</dl>
</div>
</details>"""


def _render_stored_card(contact: StoredContact) -> str:
    raw_rows = _raw_table(contact.raw, None)
    return f"""<details class="contact-card">
<summary>{escape_html(contact.display_name)}</summary>
<div class="card-body">
<dl>
<dt>Email(s)</dt><dd>{escape_html(", ".join(contact.emails) or "(none)")}</dd>
<dt>Source</dt><dd>{escape_html(contact.source or "(unknown)")}</dd>
<dt>First saved</dt><dd>{escape_html(contact.first_saved_at)}</dd>
<dt>Last saved</dt><dd>{escape_html(contact.last_saved_at)}</dd>
{raw_rows}
</dl>
</div>
</details>"""


def _render_groups(items: list, key, render_card) -> str:
    groups = group_by_first_letter(items, key)
    parts = []
    for letter, entries in groups.items():
        cards = "\n".join(render_card(entry) for entry in entries)
        parts.append(
            f'<details class="letter-group"><summary>{escape_html(letter)} ({len(entries)})</summary>\n'
            f"{cards}\n</details>"
        )
    return "\n".join(parts)


def render_upload_page(message: str | None = None) -> str:
    message_html = f'<div class="summary">{escape_html(message)}</div>' if message else ""
    body = f"""<h1>Contacts import</h1>
<p class="note">
  Pick a Google Contacts CSV export. It's parsed and compared against
  databases/app.db entirely on your own machine by this server — nothing is
  saved until you review the preview and click "Save to database".
</p>
{message_html}
<form class="upload" method="post" action="/preview" enctype="multipart/form-data">
  <input type="file" name="csv_file" accept=".csv" required>
  <input type="submit" value="Preview import">
</form>
"""
    return _page("Contacts import", body)


def render_preview_page(results: list[ClassifyResult]) -> str:
    counts = {"new": 0, "updated": 0, "unchanged": 0}
    for r in results:
        counts[r.status] += 1
    groups_html = _render_groups(results, key=lambda r: r.contact.display_name, render_card=_render_classify_card)

    payload = json.dumps([
        {
            "display_name": r.contact.display_name,
            "emails": r.contact.emails,
            "source": r.contact.source,
            "raw": r.contact.raw,
        }
        for r in results
    ])

    body = f"""<h1>Import preview</h1>
<p class="summary">
  Preview only, nothing saved yet: {counts['new']} new, {counts['updated']} would update,
  {counts['unchanged']} unchanged.
</p>
<form method="post" action="/save">
  <input type="hidden" name="contacts_json" value='{escape_html(payload)}'>
  <input type="submit" value="Save to database">
</form>
{groups_html or '<p>No contacts parsed from that file.</p>'}
"""
    return _page("Import preview", body)


def render_saved_page(counts: dict) -> str:
    body = f"""<h1>Saved</h1>
<p class="summary">
  {counts.get('new', 0)} new, {counts.get('updated', 0)} updated, {counts.get('unchanged', 0)} unchanged.
</p>
"""
    return _page("Saved", body)


def render_browse_page(contacts: list[StoredContact]) -> str:
    if not contacts:
        return _page("Browse contacts", "<h1>Browse contacts</h1><p>There are no contacts saved yet.</p>")
    groups_html = _render_groups(contacts, key=lambda c: c.display_name, render_card=_render_stored_card)
    body = f"""<h1>Browse contacts</h1>
<p class="summary">{len(contacts)} contact(s) saved.</p>
{groups_html}
"""
    return _page("Browse contacts", body)
