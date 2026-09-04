import csv
import io
import json

from contacts.demo.server import parse_csv_to_json

FIELDNAMES = ["First Name", "Last Name", "Notes", "E-mail 1 - Value"]


def _csv_text(*rows: dict) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=FIELDNAMES)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


# Synthetic fixture rows only, same convention as test_google_csv_import.py.
def test_returns_json_array_of_contacts():
    text = _csv_text({"First Name": "Alice", "Last Name": "Andersson"})
    result = json.loads(parse_csv_to_json(text))
    assert result == [{"display_name": "Alice Andersson", "emails": []}]


def test_includes_emails():
    text = _csv_text({
        "First Name": "Bo", "Last Name": "Bengtsson",
        "E-mail 1 - Value": "bo@example.com",
    })
    result = json.loads(parse_csv_to_json(text))
    assert result == [{"display_name": "Bo Bengtsson", "emails": ["bo@example.com"]}]


def test_comma_inside_a_field_does_not_break_parsing():
    text = _csv_text({
        "First Name": "Cecilia", "Last Name": "Carlsson",
        "Notes": "Referred by Bo, met at the Q3 conference",
        "E-mail 1 - Value": "cecilia@example.com",
    })
    result = json.loads(parse_csv_to_json(text))
    assert result == [{"display_name": "Cecilia Carlsson", "emails": ["cecilia@example.com"]}]
