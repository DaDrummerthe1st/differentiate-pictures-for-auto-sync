from contacts.db import ClassifyResult, StoredContact
from contacts.models import Contact
from contacts.render import (
    escape_html,
    group_by_first_letter,
    render_browse_page,
    render_field_diff,
    render_preview_page,
)

# Synthetic fixture data only, same convention as the rest of contacts/tests.


def test_escape_html_escapes_the_five_special_characters():
    assert escape_html("<b>Tom & Jerry's \"show\"</b>") == (
        "&lt;b&gt;Tom &amp; Jerry&#39;s &quot;show&quot;&lt;/b&gt;"
    )


def test_group_by_first_letter_groups_and_sorts_letters():
    items = ["Cecilia", "Alice", "Bo", "alice2"]
    groups = group_by_first_letter(items, key=lambda s: s)
    assert list(groups.keys()) == ["A", "B", "C"]
    assert groups["A"] == ["Alice", "alice2"]


def test_group_by_first_letter_uses_hash_for_blank_names():
    groups = group_by_first_letter([""], key=lambda s: s)
    assert list(groups.keys()) == ["#"]


def test_render_field_diff_shows_plain_value_when_unchanged():
    html = render_field_diff("same", "same")
    assert "diff-old" not in html
    assert "same" in html


def test_render_field_diff_highlights_old_and_new_when_changed():
    html = render_field_diff("old value", "new value")
    assert "diff-old" in html and "old value" in html
    assert "diff-new" in html and "new value" in html


def test_render_preview_page_shows_new_contact_with_new_badge():
    result = ClassifyResult(
        contact=Contact(display_name="Alice Andersson", emails=["alice@example.com"], source="google_csv"),
        status="new", matched_by=None, existing=None,
        merged_raw={}, merged_emails=["alice@example.com"],
    )
    html = render_preview_page([result])
    assert "Alice Andersson" in html
    assert "NEW" in html
    assert html.count("<details") >= 2  # letter group + contact card


def test_render_preview_page_shows_diff_for_updated_contact():
    existing = StoredContact(
        id="1", display_name="Alice Andersson", emails=["alice@example.com"],
        source="google_csv", raw={"Organization Name": "Old Co"},
        first_saved_at="t0", last_saved_at="t0",
    )
    result = ClassifyResult(
        contact=Contact(
            display_name="Alice Andersson", emails=["alice@example.com"], source="google_csv",
            raw={"Organization Name": "New Co"},
        ),
        status="updated", matched_by="email", existing=existing,
        merged_raw={"Organization Name": "New Co"}, merged_emails=["alice@example.com"],
    )
    html = render_preview_page([result])
    assert "UPDATE" in html
    assert "Old Co" in html and "New Co" in html


def test_render_preview_page_reports_summary_counts():
    new_result = ClassifyResult(
        contact=Contact(display_name="Alice", emails=[], source="google_csv"),
        status="new", matched_by=None, existing=None, merged_raw={}, merged_emails=[],
    )
    html = render_preview_page([new_result])
    assert "1 new" in html


def test_render_browse_page_lists_stored_contacts():
    stored = [
        StoredContact(
            id="1", display_name="Alice Andersson", emails=["alice@example.com"],
            source="google_csv", raw={}, first_saved_at="t0", last_saved_at="t0",
        ),
    ]
    html = render_browse_page(stored, total_count=1)
    assert "Alice Andersson" in html
    assert "alice@example.com" in html


def test_render_browse_page_on_empty_db_says_so():
    html = render_browse_page([], total_count=0)
    assert "no contacts" in html.lower()


def test_render_browse_page_shows_search_form_with_field_checkboxes():
    html = render_browse_page(
        [], total_count=5, query="", selected_fields=["display_name", "emails"],
        available_fields=["display_name", "emails", "Organization Name"],
    )
    assert '<form' in html
    assert 'name="q"' in html
    assert 'value="Organization Name"' in html
    assert 'name="field" value="display_name" checked' in html
    assert 'name="field" value="Organization Name"' in html
    assert 'name="field" value="Organization Name" checked' not in html


def test_render_browse_page_groups_field_checkboxes_into_collapsed_categories():
    html = render_browse_page(
        [], total_count=5, query="", selected_fields=["display_name", "emails"],
        available_fields=["display_name", "emails", "Organization Name", "Middle Name", "Birthday"],
    )
    # Categories render as native <details>, collapsed by default (no "open" attribute
    # on any of them - "Contact info", "Organization" etc. must not auto-expand).
    assert "<summary>Basic</summary>" in html
    assert "<summary>Organization</summary>" in html
    assert "<summary>Name details</summary>" in html
    assert "<summary>Other</summary>" in html
    assert "<details open" not in html


def test_render_browse_page_shows_no_match_message_when_search_finds_nothing():
    html = render_browse_page([], total_count=5, query="nobody-has-this-name")
    assert "no contacts match" in html.lower()
    # Distinguishes "no results for this search" from "database is empty".
    assert "no contacts saved yet" not in html.lower()


def test_render_browse_page_shows_count_summary():
    stored = [
        StoredContact(
            id="1", display_name="Alice Andersson", emails=[],
            source="google_csv", raw={}, first_saved_at="t0", last_saved_at="t0",
        ),
    ]
    html = render_browse_page(stored, total_count=5, query="alice")
    assert "1" in html and "5" in html
