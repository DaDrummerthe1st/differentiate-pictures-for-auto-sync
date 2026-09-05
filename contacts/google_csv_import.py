import csv
import io
import re

from contacts.models import Contact

_EMAIL_VALUE_COLUMN = re.compile(r"^E-mail \d+ - Value$")


def parse_google_csv(csv_text: str) -> list[Contact]:
    """Parse Google Contacts' CSV export format into normalized Contact records.

    A convenience importer for the one provider Joakim already has an export
    from — the vCard importer (vcard_import.py) is the actually provider-agnostic
    path; this one exists because not every user will know how to export vCard
    instead of the default CSV.
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    contacts = []
    for row in reader:
        display_name = " ".join(
            part for part in (row.get("First Name"), row.get("Last Name")) if part
        )
        emails = [
            value
            for key, value in row.items()
            if _EMAIL_VALUE_COLUMN.match(key) and value
        ]
        contacts.append(
            Contact(display_name=display_name, emails=emails, source="google_csv", raw=dict(row))
        )
    return contacts
