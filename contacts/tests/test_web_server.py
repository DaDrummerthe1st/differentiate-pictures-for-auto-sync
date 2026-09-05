import csv
import io

from contacts.db import list_all_contacts, save_contacts
from contacts.models import Contact
from contacts.web.server import handle_browse, handle_preview, handle_save

FIELDNAMES = ["First Name", "Last Name", "Notes", "E-mail 1 - Value"]


def _csv_text(*rows: dict) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=FIELDNAMES)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


# Synthetic fixture rows only, same convention as test_google_csv_import.py.
def test_handle_preview_renders_parsed_contacts_without_saving(tmp_path):
    db_path = str(tmp_path / "app.db")
    text = _csv_text({"First Name": "Alice", "Last Name": "Andersson"})

    html = handle_preview(text.encode("utf-8"), db_path=db_path)

    assert "Alice Andersson" in html
    assert "NEW" in html
    assert list_all_contacts(db_path=db_path) == []


def test_handle_preview_handles_comma_inside_a_field(tmp_path):
    html = handle_preview(
        _csv_text({
            "First Name": "Cecilia", "Last Name": "Carlsson",
            "Notes": "Referred by Bo, met at the Q3 conference",
            "E-mail 1 - Value": "cecilia@example.com",
        }).encode("utf-8"),
        db_path=str(tmp_path / "app.db"),
    )
    assert "Cecilia Carlsson" in html
    assert "cecilia@example.com" in html


def test_handle_save_persists_contacts_from_json_payload(tmp_path):
    db_path = str(tmp_path / "app.db")
    payload = (
        '[{"display_name": "Alice Andersson", "emails": ["alice@example.com"], '
        '"source": "google_csv", "raw": {}}]'
    )

    html = handle_save(payload, db_path=db_path)

    assert "1" in html
    stored = list_all_contacts(db_path=db_path)
    assert stored[0].display_name == "Alice Andersson"


def test_handle_browse_lists_saved_contacts(tmp_path):
    db_path = str(tmp_path / "app.db")
    save_contacts(
        [Contact(display_name="Alice Andersson", emails=["alice@example.com"], source="google_csv")],
        db_path=db_path,
    )

    html = handle_browse(db_path=db_path)

    assert "Alice Andersson" in html


def test_handle_browse_on_empty_db_says_so(tmp_path):
    html = handle_browse(db_path=str(tmp_path / "app.db"))
    assert "no contacts" in html.lower()
