import json
import sqlite3

from contacts.db import classify_contacts, list_all_contacts, save_contacts
from contacts.models import Contact

# Synthetic fixture data only, same convention as the rest of contacts/tests.


def test_new_contact_with_email_is_inserted(tmp_path):
    db_path = tmp_path / "app.db"
    results = save_contacts(
        [Contact(display_name="Alice Andersson", emails=["alice@example.com"], source="google_csv")],
        db_path=str(db_path),
    )

    assert results[0].status == "new"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM contacts").fetchone()
    assert row["display_name"] == "Alice Andersson"
    emails = [r["email"] for r in conn.execute("SELECT email FROM contact_emails")]
    assert emails == ["alice@example.com"]
    conn.close()


def test_reimporting_identical_contact_is_unchanged(tmp_path):
    db_path = tmp_path / "app.db"
    contact = Contact(display_name="Alice Andersson", emails=["alice@example.com"], source="google_csv")
    save_contacts([contact], db_path=str(db_path))

    results = save_contacts([contact], db_path=str(db_path))

    assert results[0].status == "unchanged"


def test_matching_email_updates_existing_contact_instead_of_duplicating(tmp_path):
    db_path = tmp_path / "app.db"
    save_contacts(
        [Contact(display_name="Alice Andersson", emails=["alice@example.com"], source="google_csv")],
        db_path=str(db_path),
    )

    results = save_contacts(
        [Contact(display_name="Alice A.", emails=["alice@example.com"], source="google_csv")],
        db_path=str(db_path),
    )

    assert results[0].status == "updated"
    assert results[0].matched_by == "email"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM contacts").fetchall()
    assert len(rows) == 1
    assert rows[0]["display_name"] == "Alice A."
    conn.close()


def test_no_email_falls_back_to_matching_by_exact_display_name(tmp_path):
    db_path = tmp_path / "app.db"
    save_contacts(
        [Contact(display_name="Cecilia Carlsson", emails=[], source="google_csv")],
        db_path=str(db_path),
    )

    results = save_contacts(
        [Contact(display_name="Cecilia Carlsson", emails=[], source="google_csv", raw={"Notes": "met at conf"})],
        db_path=str(db_path),
    )

    assert results[0].status == "updated"
    assert results[0].matched_by == "display_name"


def test_no_email_and_different_display_name_is_a_new_contact(tmp_path):
    db_path = tmp_path / "app.db"
    save_contacts(
        [Contact(display_name="Cecilia Carlsson", emails=[], source="google_csv")],
        db_path=str(db_path),
    )

    results = save_contacts(
        [Contact(display_name="Someone Else", emails=[], source="google_csv")],
        db_path=str(db_path),
    )

    assert results[0].status == "new"
    assert results[0].matched_by is None


def test_merge_combines_raw_fields_from_both_imports_not_just_email_and_name(tmp_path):
    db_path = tmp_path / "app.db"
    save_contacts(
        [Contact(
            display_name="Alice Andersson", emails=["alice@example.com"], source="google_csv",
            raw={"Organization Name": "Acme"},
        )],
        db_path=str(db_path),
    )

    save_contacts(
        [Contact(
            display_name="Alice Andersson", emails=["alice@example.com"], source="google_csv",
            raw={"Notes": "Met at conf"},
        )],
        db_path=str(db_path),
    )

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT raw FROM contacts").fetchone()
    merged = json.loads(row["raw"])
    assert merged["Organization Name"] == "Acme"
    assert merged["Notes"] == "Met at conf"
    conn.close()


def test_merge_prefers_the_newer_imports_value_when_a_raw_field_conflicts(tmp_path):
    db_path = tmp_path / "app.db"
    save_contacts(
        [Contact(
            display_name="Alice Andersson", emails=["alice@example.com"], source="google_csv",
            raw={"Organization Name": "Old Co"},
        )],
        db_path=str(db_path),
    )

    save_contacts(
        [Contact(
            display_name="Alice Andersson", emails=["alice@example.com"], source="google_csv",
            raw={"Organization Name": "New Co"},
        )],
        db_path=str(db_path),
    )

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT raw FROM contacts").fetchone()
    assert json.loads(row["raw"])["Organization Name"] == "New Co"
    conn.close()


def test_merge_unions_emails_instead_of_replacing_them(tmp_path):
    db_path = tmp_path / "app.db"
    save_contacts(
        [Contact(display_name="Bo Bengtsson", emails=["bo@work.example.com"], source="google_csv")],
        db_path=str(db_path),
    )
    # Matched by display_name (no shared email yet) but brings a new email in.
    save_contacts(
        [Contact(display_name="Bo Bengtsson", emails=["bo.b@example.com"], source="google_csv")],
        db_path=str(db_path),
    )

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    emails = {r["email"] for r in conn.execute("SELECT email FROM contact_emails")}
    assert emails == {"bo@work.example.com", "bo.b@example.com"}
    conn.close()


def test_classify_previews_without_writing_anything(tmp_path):
    db_path = tmp_path / "app.db"
    save_contacts(
        [Contact(display_name="Alice Andersson", emails=["alice@example.com"], source="google_csv")],
        db_path=str(db_path),
    )

    results = classify_contacts(
        [Contact(display_name="Alice A.", emails=["alice@example.com"], source="google_csv")],
        db_path=str(db_path),
    )

    assert results[0].status == "updated"
    assert results[0].matched_by == "email"
    # Still says "Alice Andersson" - classify must not have written the rename.
    conn = sqlite3.connect(str(db_path))
    row = conn.execute("SELECT display_name FROM contacts").fetchone()
    assert row[0] == "Alice Andersson"
    conn.close()


def test_classify_new_contact_has_no_existing_record(tmp_path):
    db_path = tmp_path / "app.db"
    results = classify_contacts(
        [Contact(display_name="Someone New", emails=["new@example.com"], source="google_csv")],
        db_path=str(db_path),
    )
    assert results[0].status == "new"
    assert results[0].existing is None


def test_classify_reports_merged_raw_and_emails_preview(tmp_path):
    db_path = tmp_path / "app.db"
    save_contacts(
        [Contact(
            display_name="Alice Andersson", emails=["alice@example.com"], source="google_csv",
            raw={"Organization Name": "Acme"},
        )],
        db_path=str(db_path),
    )

    results = classify_contacts(
        [Contact(
            display_name="Alice Andersson", emails=["alice2@example.com"], source="google_csv",
            raw={"Notes": "Met at conf"},
        )],
        db_path=str(db_path),
    )

    assert results[0].merged_raw == {"Organization Name": "Acme", "Notes": "Met at conf"}
    assert set(results[0].merged_emails) == {"alice@example.com", "alice2@example.com"}


def test_list_all_contacts_returns_stored_contacts_with_emails(tmp_path):
    db_path = tmp_path / "app.db"
    save_contacts(
        [
            Contact(display_name="Alice Andersson", emails=["alice@example.com"], source="google_csv"),
            Contact(display_name="Bo Bengtsson", emails=[], source="vcard"),
        ],
        db_path=str(db_path),
    )

    stored = list_all_contacts(db_path=str(db_path))

    by_name = {c.display_name: c for c in stored}
    assert by_name["Alice Andersson"].emails == ["alice@example.com"]
    assert by_name["Bo Bengtsson"].emails == []
    assert by_name["Bo Bengtsson"].source == "vcard"


def test_list_all_contacts_on_empty_db_returns_empty_list(tmp_path):
    db_path = tmp_path / "app.db"
    assert list_all_contacts(db_path=str(db_path)) == []
