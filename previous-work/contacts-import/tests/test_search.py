from contacts.db import StoredContact
from contacts.search import available_search_fields, categorize_fields, filter_contacts

# Synthetic fixture data only, same convention as the rest of contacts/tests.


def _contact(display_name, emails=None, raw=None):
    return StoredContact(
        id="id-" + display_name, display_name=display_name, emails=emails or [],
        source="google_csv", raw=raw or {}, first_saved_at="t0", last_saved_at="t0",
    )


def test_empty_query_returns_everything():
    contacts = [_contact("Alice Andersson"), _contact("Bo Bengtsson")]
    assert filter_contacts(contacts, query="", fields=["display_name"]) == contacts


def test_matches_display_name_case_insensitively():
    contacts = [_contact("Alice Andersson"), _contact("Bo Bengtsson")]
    result = filter_contacts(contacts, query="alice", fields=["display_name"])
    assert result == [contacts[0]]


def test_matches_any_email():
    contacts = [
        _contact("Alice Andersson", emails=["alice@example.com"]),
        _contact("Bo Bengtsson", emails=["bo@work.example.com"]),
    ]
    result = filter_contacts(contacts, query="work", fields=["emails"])
    assert result == [contacts[1]]


def test_matches_a_raw_field_when_selected():
    contacts = [
        _contact("Alice Andersson", raw={"Organization Name": "Acme"}),
        _contact("Bo Bengtsson", raw={"Organization Name": "Globex"}),
    ]
    result = filter_contacts(contacts, query="acme", fields=["Organization Name"])
    assert result == [contacts[0]]


def test_does_not_match_a_field_that_is_not_selected():
    # "Andersson" only appears in display_name, not in the email address -
    # searching "emails" only must not fall through to display_name.
    contacts = [_contact("Alice Andersson", emails=["alice@example.com"])]
    result = filter_contacts(contacts, query="andersson", fields=["emails"])
    assert result == []


def test_no_fields_selected_matches_nothing_once_a_query_is_given():
    contacts = [_contact("Alice Andersson")]
    assert filter_contacts(contacts, query="alice", fields=[]) == []


def test_available_search_fields_includes_display_name_and_emails_plus_raw_keys():
    contacts = [
        _contact("Alice Andersson", raw={"Organization Name": "Acme"}),
        _contact("Bo Bengtsson", raw={"Notes": "met at conf"}),
    ]
    fields = available_search_fields(contacts)
    assert fields[:2] == ["display_name", "emails"]
    assert "Organization Name" in fields
    assert "Notes" in fields


def test_categorize_fields_puts_display_name_and_emails_in_basic():
    categories = categorize_fields(["display_name", "emails"])
    assert categories["Basic"] == ["display_name", "emails"]


def test_categorize_fields_groups_organization_columns():
    fields = ["display_name", "emails", "Organization Name", "Organization Title"]
    categories = categorize_fields(fields)
    assert categories["Organization"] == ["Organization Name", "Organization Title"]
    assert "Organization Name" not in categories.get("Other", [])


def test_categorize_fields_groups_contact_info_columns():
    fields = ["E-mail 1 - Value", "Phone 1 - Value", "Address 1 - Formatted", "Website 1 - Value"]
    categories = categorize_fields(fields)
    assert set(categories["Contact info"]) == set(fields)


def test_categorize_fields_groups_name_detail_columns():
    fields = ["Middle Name", "Nickname", "Name Prefix", "File As"]
    categories = categorize_fields(fields)
    assert set(categories["Name details"]) == set(fields)


def test_categorize_fields_puts_unrecognized_columns_in_other():
    categories = categorize_fields(["Birthday", "Notes", "Custom Field 1 - Value"])
    assert set(categories["Other"]) == {"Birthday", "Notes", "Custom Field 1 - Value"}


def test_categorize_fields_every_input_field_appears_exactly_once():
    fields = [
        "display_name", "emails", "Organization Name", "E-mail 1 - Value",
        "Middle Name", "Birthday",
    ]
    categories = categorize_fields(fields)
    all_categorized = [f for group in categories.values() for f in group]
    assert sorted(all_categorized) == sorted(fields)


def test_available_search_fields_has_no_duplicates():
    contacts = [
        _contact("Alice Andersson", raw={"Organization Name": "Acme"}),
        _contact("Bo Bengtsson", raw={"Organization Name": "Globex"}),
    ]
    fields = available_search_fields(contacts)
    assert fields.count("Organization Name") == 1
