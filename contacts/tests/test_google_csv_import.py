import csv
import io

from contacts.google_csv_import import parse_google_csv

FIELDNAMES = [
    "First Name", "Middle Name", "Last Name", "Phonetic First Name",
    "Phonetic Middle Name", "Phonetic Last Name", "Name Prefix", "Name Suffix",
    "Nickname", "File As", "Organization Name", "Organization Title",
    "Organization Department", "Birthday", "Notes", "Photo", "Labels",
    "E-mail 1 - Label", "E-mail 1 - Value", "E-mail 2 - Label", "E-mail 2 - Value",
]


def _csv_text(*rows: dict) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=FIELDNAMES)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


# Synthetic fixture rows only — fake names/emails, never a real exported file.
def test_parses_first_and_last_name_into_display_name():
    text = _csv_text({"First Name": "Alice", "Last Name": "Andersson"})
    contacts = parse_google_csv(text)
    assert contacts[0].display_name == "Alice Andersson"


def test_parses_single_email():
    text = _csv_text({
        "First Name": "Alice", "Last Name": "Andersson",
        "E-mail 1 - Value": "alice@example.com",
    })
    contacts = parse_google_csv(text)
    assert contacts[0].emails == ["alice@example.com"]


def test_parses_multiple_numbered_email_columns():
    text = _csv_text({
        "First Name": "Bo", "Last Name": "Bengtsson",
        "E-mail 1 - Value": "bo.b@example.com",
        "E-mail 2 - Value": "bo@work.example.com",
    })
    contacts = parse_google_csv(text)
    assert contacts[0].emails == ["bo.b@example.com", "bo@work.example.com"]


def test_contact_with_no_email_gets_empty_list():
    text = _csv_text({"First Name": "Cecilia", "Last Name": "Carlsson"})
    contacts = parse_google_csv(text)
    assert contacts[0].emails == []


def test_tags_source_as_google_csv():
    text = _csv_text({"First Name": "Alice", "Last Name": "Andersson"})
    contacts = parse_google_csv(text)
    assert contacts[0].source == "google_csv"


def test_parses_multiple_rows():
    text = _csv_text(
        {"First Name": "Alice", "Last Name": "Andersson"},
        {"First Name": "Bo", "Last Name": "Bengtsson"},
    )
    contacts = parse_google_csv(text)
    assert len(contacts) == 2
