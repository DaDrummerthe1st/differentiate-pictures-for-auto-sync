from contacts.vcard_import import parse_vcard

# Synthetic fixture data only — fake names/emails, never a real exported file.
SAMPLE_VCARD = """BEGIN:VCARD
VERSION:3.0
FN:Alice Andersson
EMAIL:alice@example.com
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Bo Bengtsson
EMAIL:bo.b@example.com
EMAIL:bo@work.example.com
END:VCARD
"""


def test_parses_display_name_and_email():
    contacts = parse_vcard(SAMPLE_VCARD)
    assert contacts[0].display_name == "Alice Andersson"
    assert contacts[0].emails == ["alice@example.com"]


def test_parses_multiple_emails_on_one_contact():
    contacts = parse_vcard(SAMPLE_VCARD)
    assert contacts[1].emails == ["bo.b@example.com", "bo@work.example.com"]


def test_parses_multiple_vcards_in_one_file():
    contacts = parse_vcard(SAMPLE_VCARD)
    assert len(contacts) == 2


def test_tags_source_as_vcard():
    contacts = parse_vcard(SAMPLE_VCARD)
    assert contacts[0].source == "vcard"


def test_contact_with_no_email_gets_empty_list():
    vcard = "BEGIN:VCARD\nVERSION:3.0\nFN:No Email Nilsson\nEND:VCARD\n"
    contacts = parse_vcard(vcard)
    assert contacts[0].emails == []


def test_raw_captures_other_vcard_properties_for_whole_record_comparison():
    vcard = (
        "BEGIN:VCARD\nVERSION:3.0\nFN:Alice Andersson\nEMAIL:alice@example.com\n"
        "ORG:Acme\nNOTE:Met at conf\nEND:VCARD\n"
    )
    contacts = parse_vcard(vcard)
    assert contacts[0].raw["ORG"] == "Acme"
    assert contacts[0].raw["NOTE"] == "Met at conf"
