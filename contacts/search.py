"""Text search over the browse-all-contacts page (contacts/web/server.py's
GET /contacts). Deliberately field-scoped rather than free-text-over-
everything: Joakim wants to pick which fields a search actually looks in
(display name and emails by default; any other field captured in a
contact's `raw` record is available too), not a fixed always-search-
everything box.
"""
from contacts.db import StoredContact

# Always offered first, before whatever raw field names happen to exist -
# these are the two fields every contact has, regardless of source.
_BUILTIN_FIELDS = ["display_name", "emails"]

# What a browse-page request searches in when it hasn't submitted its own
# field selection yet (a fresh GET /contacts, no query string at all).
DEFAULT_SEARCH_FIELDS = list(_BUILTIN_FIELDS)


def available_search_fields(contacts: list[StoredContact]) -> list[str]:
    raw_keys: dict[str, None] = {}
    for contact in contacts:
        for key in contact.raw:
            raw_keys[key] = None
    return _BUILTIN_FIELDS + sorted(raw_keys)


def _field_value(contact: StoredContact, field: str) -> str:
    if field == "display_name":
        return contact.display_name
    if field == "emails":
        return ", ".join(contact.emails)
    return str(contact.raw.get(field, ""))


def filter_contacts(contacts: list[StoredContact], query: str, fields: list[str]) -> list[StoredContact]:
    if not query:
        return list(contacts)
    needle = query.lower()
    return [
        contact for contact in contacts
        if any(needle in _field_value(contact, field).lower() for field in fields)
    ]
